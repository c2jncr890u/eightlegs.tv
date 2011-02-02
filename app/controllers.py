# -*- coding: utf-8 -*-

import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gdata.youtube
import gdata.youtube.service
import json
import random
import re
import smtplib
import string
import tornado.database
import tornado.escape
import tornado.web


###########################################
#     MODELS
###########################################

RE_EMAIL    = re.compile(r"^[-a-z0-9_]+@([-a-z0-9]+\.)+[a-z]{2,6}$",re.IGNORECASE)

db = tornado.database.Connection(
         host="127.0.0.1:3306", database="eightlegs",
         user="root", password=file('/var/eightlegs.tv/app/secrets/database_key').read().strip(),
         max_idle_time=7*3600
)

def u2id( u ): 
    db.execute("INSERT IGNORE users(u) values(%s)",u)
    return db.get("SELECT id FROM users WHERE u=%s",u).id
def q2id( q ): 
    q = tornado.escape.squeeze(q).lower()
    db.execute("INSERT IGNORE queries(q) values(%s)",q)
    return db.get("SELECT id FROM queries WHERE q=%s",q).id
def v2id( u ): 
    db.execute("INSERT IGNORE videos(v) values(%s)",v)
    return db.get("SELECT id FROM videos WHERE v=%s",v).id

###########################################
#     YOUTUBE API CALLS
###########################################

def youtube_service():
   yt_service = gdata.youtube.service.YouTubeService()
   yt_service.developer_key = file('/var/eightlegs.tv/app/secrets/developer_key').read().strip()
   yt_service.client_id = 'eightlegs.tv'
   return yt_service

def youtube_search( q ):
   yt_service = youtube_service()
   query = gdata.youtube.service.YouTubeVideoQuery()
   query.vq = tornado.escape.utf8(q)
   query.orderby = 'relevance'
   query.racy = 'include'
   query.max_results = '1'
   query.start_index = random.randint(1,30)
   feed = yt_service.YouTubeQuery(query)
   for entry in feed.entry:
      return entry.id.text.rsplit('/',1)[1]
   return ''

def youtube_related( v ):
   yt_service = youtube_service()
   feed = yt_service.GetYouTubeRelatedVideoFeed(video_id=v)
   return random.choice(feed.entry).id.text.rsplit('/',1)[1]


############################################
#   RECOMMENDATION ENGINE
############################################

def recommend( uid, qid, q ):
    count = db.get("SELECT count(*) FROM playlists WHERE uid=%s AND qid=%s",uid,qid)["count(*)"]
    if count <= random.randint(0,3):
        seedv = youtube_search(q)
    else:
        seedid = db.get("SELECT vid FROM playlists WHERE uid=%s AND qid=%s LIMIT %s,1",uid,qid,random.randint(0,count-1)).vid
        seedv  = db.get("SELECT v FROM videos WHERE id=%s",seedid).v
    return youtube_related(seedv) 


############################################
#   CONTROLLERS
############################################

class AuthHandler( tornado.web.RequestHandler ):
    def uid( self ):
        return u2id( self.get_secure_cookie("user") or str(self.request.remote_ip) )
    def current_user( self ):
        return self.get_secure_cookie("user")
            
class signin( AuthHandler ):
    def get( self ):
        self.render("signin.html", q="")
    def post( self ):
        log = self.get_argument("log")
        pwd = self.get_argument("pwd")
        user = db.get("SELECT * from users where u=%s and pwdhash=SHA1(CONCAT(%s,%s))",log,log,pwd)
        if user:
            self.set_secure_cookie("user",user.u)
            self.redirect("/recent")
        else:
            self.redirect("/signin?error=signin")

class signout( AuthHandler ):
    def get( self ):
        self.clear_cookie("user")
        self.redirect("/signin")

text_template = "Please confirm your Eightlegs.tv account by clicking this link: http://eightlegs.tv/confirm?id={pk}"
html_template = """\
<html>
  <head></head>
  <body>
    <div lang="en" style="background-color:#fff;color:#222">
        <div style="padding:14px;margin-bottom:4px;background-color:#000;color:#f00">
            <a href="email_header" target="_blank"><img alt="Eightlegs.tv" height="24" src="logo_overlay" style="display:block;border:0" width="130"></a>
        </div>
        <div style="font-family:'Helvetica Neue', Arial, Helvetica, sans-serif;font-size:13px;margin:14px">
            <p>
                Please confirm your Eightlegs.tv account by clicking this link:<br>
                <a href="http://eightlegs.tv/confirm?id={pk}" target="_blank">http://eightlegs.tv/confirm?id={pk}</a>
            </p>
        </div>
        </div>
  </body>
</html>
"""
class signup( AuthHandler ):
    def get( self ):
        self.render("signup.html", q="")
    def post( self ):
        log = self.get_argument('log')
        pwd = self.get_argument('pwd')
        if not RE_EMAIL.match(log): return self.redirect("/signup?error=email")
        pk = ''.join(random.choice(string.letters) for _ in range(20))
        expires = datetime.datetime.now() + datetime.timedelta(minutes=30)
        js = json.dumps({ 'action':'confirm_signup', 'log': log, 'pwd': pwd })
        db.execute("INSERT IGNORE tmp (pk,expires,json) values (%s,%s,%s)",pk,expires,js)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Confirm your account at eightlegs.tv"
        msg['From'] = 'noreply@eightlegs.tv'
        msg['To'] = log
        msg.attach( MIMEText(text_template.format(pk=pk), 'plain') )
        msg.attach( MIMEText(html_template.format(pk=pk), 'html') )

        s = smtplib.SMTP()
        s.connect("localhost")
        s.sendmail("noreply@eightlegs.tv",log, msg.as_string())
        s.close()

class index( AuthHandler ):
    def get( self ):
        q = random.choice(kickstarter_queries)
        v = recommend( self.uid(), q2id(q), q )
        self.redirect( "/player?v=%s&q=%s" % (v,tornado.escape.url_escape(q)) )

class player( AuthHandler ):
    def get( self ):
        v = self.get_argument("v",None)
        q = self.get_argument("q","")
        if v==None:
            if q=="":
                q = random.choice(kickstarter_queries)
            v = recommend( self.uid(), q2id(q), q )
            self.redirect( "/player?v=%s&q=%s" % (v,tornado.escape.url_escape(q)) )
        else:
            self.render( "player.html", v=v, q=q, escape=tornado.escape )


#http://en.wikipedia.org/wiki/List_of_best-selling_music_artists
kickstarter_queries = (
   "The Beatles", "Elvis Presley", "Michael Jackson", "ABBA", "Madonna",
   "Led Zeppelin", "Queen", "AC/DC", "Bee Gees", "Celine Dion", "Elton John",
   "Julio Iglesias", "Mariah Carey", "Nana Mouskouri", "Pink Floyd", "The Rolling Stones",
   "Aerosmith", "A. R. Rahman", "Backstreet Boys", "Barbra Streisand", "Barry White",
   "Billy Joel", "Boney M.", "Bon Jovi", "Britney Spears", "Bruce Springsteen",
   "Bryan Adams", "The Carpenters", "Charles Aznavour", "Cher", "Chicago", "David Bowie",
   "Deep Purple", "Depeche Mode", "Dire Straits", "Dolly Parton", "Eagles", "Fleetwood Mac",
   "Frank Sinatra", "Garth Brooks", "Genesis", "George Michael", "Guns N' Roses", "The Jackson 5",
   "Janet Jackson", "Johnny Hallyday", "Kenny Rogers", "Kiss", "Lionel Richie", "Luciano Pavarotti",
   "Metallica", "Michiya Mihashi", "Modern Talking", "Neil Diamond", "Olivia Newton-John", 
   "Paul McCartney", "Perry Como", "Pet Shop Boys", "Phil Collins", "Roberto Carlos", 
   "Rod Stewart", "Scorpions", "Status Quo", "Stevie Wonder", "Tina Turner", "U2", "Whitney Houston",
   "The Who", "B'z", "Carlos Santana", "Eminem", "Eurythmics", "Gloria Estefan", "Iron Maiden", 
   "Journey", "Luis Miguel", "Prince", "Spice Girls", "Tupac Shakur", "Van Halen", "Ace of Base",
   "Alan Jackson", "Alice Cooper", "Andrea Bocelli", "Anne Murray", "Ayumi Hamasaki", "Beyoncé",
   "Black Eyed Peas", "Black Sabbath", "Bob Dylan", "Bob Seger", "Boyz II Men", "Coldplay",
   "Def Leppard", "Destiny's Child", "Dreams Come True", "Duran Duran", "Enya", "Four Tops",
   "George Strait", "Glay", "Green Day", "Hibari Misora", "James Last", "Jay-Z", "Jean Michel Jarre",
   "Jethro Tull", "Johnny Cash", "Kenny G", "Kylie Minogue", "Lady Gaga", "Linkin Park", "Meat Loaf",
   "Michael Bolton", "Mötley Crüe", "Mr.Children", "Nat King Cole", "New Kids on the Block", 
   "Nirvana", "Oasis", "Orhan Gencebay", "Pearl Jam", "The Police", "Ray Conniff", "Reba McEntire",
   "Red Hot Chili Peppers", "R.E.M.", "Ricky Martin", "Rihanna", "Robbie Williams", "Roxette",
   "Sade", "Shakira", "Shania Twain", "Tom Petty and the Heartbreakers", "Tony Bennett", "UB40",
   "Hikaru Utada", "Vicente Fernández", "Village People", "Willie Nelson",
)






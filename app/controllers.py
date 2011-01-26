
from email.MIMEText import MIMEText
import os.path
import random
import smtplib
import string
import subprocess
import tornado.web


###########################################
#     MODELS
###########################################

db = tornado.database.Connection(
         host="127.0.0.1:3306", database="eightlegs",
         user="root", password=file('/var/eightlegs.tv/secret/database_key').read().strip(),
         max_idle_time=7*3600
)

def u2id( u ): 
    db.execute("INSERT IGNORE users(u) values(%s)",u)
    return db.query("SELECT id FROM users WHERE u=%s",u).id
def q2id( q ): 
    q = tornado.escape.squeeze(q).lower()
    db.execute("INSERT IGNORE queries(q) values(%s)",q)
    return db.query("SELECT id FROM queries WHERE q=%s",q).id
def v2id( u ): 
    db.execute("INSERT IGNORE videos(v) values(%s)",v)
    return db.query("SELECT id FROM videos WHERE v=%s",v).id

###########################################
#     YOUTUBE API CALLS
###########################################

import gdata.youtube
import gdata.youtube.service

def youtube_service():
   yt_service = gdata.youtube.service.YouTubeService()
   yt_service.developer_key = file('/var/eightlegs.tv/secret/developer_key').read().strip()
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
    count = db.get("SELECT count(*) FROM opinions WHERE uid=%s AND qid=%s",uid,qid)["count(*)"]
    if count < random.randint(0,3):
        seedv = youtube_search(q)
    else:
        seedid = db.get("SELECT vid FROM opinions WHERE uid=%s AND qid=%s LIMIT %s,1",uid,qid,random.randint(0,count-1)).vid
        seedv  = db.get("SELECT v FROM videos WHERE id=%s",seedid).v
    return youtube_related(seedv) 


############################################
#   CONTROLLERS
############################################

class AuthHandler( tornado.web.RequestHandler ):
    def uid( self ):
        pass #beware of cookies failing at two levels

class index( AuthHandler ):
    def get( self ):
        q = random.choice(kickstarter_queries)
        v = recommend( self.uid(), q2id(q), q )
        self.redirect( "/player?v=%s&q=%s" % (v,q) )

class player( AuthHandler ):
    def get( self ):
        v = self.get_argument("v",None)
        q = self.get_argument("q","")
        if v==None:
            if q=="":
                q = random.choice(kickstarter_queries)
            v = recommend( self.uid(), q2id(q), q )
        self.render( "player.html", v=v, q=q )


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






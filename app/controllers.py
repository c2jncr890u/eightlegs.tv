
from email.MIMEText import MIMEText
import os.path
import random
import smtplib
import string
import subprocess
import tornado.web


class index( tornado.web.RequestHandler ):
    def get( self ):
        self.redirect( "/player?v=%s&q=%s" )

class about( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "about.html" )

class contact( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "contact.html" )

class terms( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "terms.html" )

class privacy( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "privacy.html" )







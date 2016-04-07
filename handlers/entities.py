from google.appengine.ext import ndb
import json
from constants import *
import datetime


class Visitor(ndb.Model):
	ip = ndb.StringProperty()
	added_on = ndb.DateTimeProperty(auto_now_add=True)



class event(ndb.Model):
	pass


class account(ndb.Model):
	username = ndb.StringProperty(required=True)
	email = ndb.StringProperty()
	password = ndb.StringProperty(required=True)
	groups = ndb.KeyProperty(repeated=True , kind = event)



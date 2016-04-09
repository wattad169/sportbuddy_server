from google.appengine.ext import ndb
import json
from constants import *


class Visitor(ndb.Model):
	ip = ndb.StringProperty()
	added_on = ndb.DateTimeProperty(auto_now_add=True)



class event(ndb.Model):
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty(required=True)
	date = ndb.DateTimeProperty()
	location = ndb.GeoPtProperty()
	members = ndb.KeyProperty(repeated=True , kind = 'account')
	created_by = ndb.KeyProperty(kind = 'account')
	formatted_location = ndb.StringProperty(required=True)

	def custom_to_dict(self):
		return {
			'id': self.key.id(),
			'members': [key.urlsafe() for key in self.members],
			'created_by' : self.created_by.urlsafe(),
			'location':{'lat': self.location.lat, 'lon': self.location.lon},
			'formatted_location':self.formatted_location,
			'name':self.name,
			'type':self.type,
			'date':self.date.isoformat()
		}


class account(ndb.Model):
	username = ndb.StringProperty(required=True)
	email = ndb.StringProperty()
	password = ndb.StringProperty(required=True)
	events = ndb.KeyProperty(repeated=True , kind = 'event')



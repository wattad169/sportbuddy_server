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
	from_time = ndb.StringProperty()
	end_time = ndb.StringProperty()
	description = ndb.StringProperty()
	min_attend = ndb.StringProperty()
	max_attend = ndb.StringProperty()

	def custom_to_dict(self):
		return {
			'id': self.key.id(),
			'members': [key.id() for key in self.members],
			'created_by' : self.created_by.id(),
			'location':{'lat': self.location.lat, 'lon': self.location.lon},
			'formatted_location':self.formatted_location,
			'name':self.name,
			'type':self.type,
			'date':str(self.date.isoformat())[:str(self.date.isoformat()).find('T')],
			'from_time':self.from_time,
			'end_time':self.end_time,
			'description':self.description,
			'min_attend' : self.min_attend,
			'max_attend' : self.max_attend
		}


class account(ndb.Model):
	fullname = ndb.StringProperty(required=True)
	facebook_id = ndb.StringProperty()
	google_id = ndb.StringProperty()
	photo = ndb.BlobProperty(required=True)
	photo_url = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty()
	events = ndb.KeyProperty(repeated=True , kind = 'event')
	notifications_token = ndb.StringProperty()
	def custom_to_dict(self):
		return {
			'id': self.key.id(),
			'events': [key.id() for key in self.events],
			'fullname' : self.fullname,
			'email' : self.email,
			'photo' : self.photo,
			'photo_url' : self.photo_url
		}



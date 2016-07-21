from constants import *
import json
import urllib2
import httplib
import constants
import logging
from entities import *
from google.appengine.ext import ndb
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
def to_json(query):
	return [dict(p.to_dict(exclude=['added_on']), **dict(id=p.key.id())) for p in query]



def create_response(status,response_body):
	result = {}
	if(status==OK):
		result[STATUS] = OK
	else:
		result[STATUS] = NOK

	result[MESSAGE] = response_body

	return json.dumps(result)

def get_geoaddrees_by_coordinates(lon,lat):
	get_location = "{0}{1},{2}&key={3}".format(GEOCOODING_URL_PREFIX,lon,lat,SERVER_API_KEY)
	response = urllib2.urlopen(get_location)
	data = json.load(response)
	return data["results"][0]["formatted_address"]

def send_notifcation_to_user(notifcation_token,title,message,moreParams=None):
	TAG = "SEND_NOTIFICATION_TO_USER"
	conn = httplib.HTTPSConnection("android.googleapis.com")
	conn.connect()
	body = {}
	notifcation = {}
	notifcation['message'] = message
	notifcation['title'] = title
	if moreParams!=None:
		moredict = {"more":[moreParams]}
		notifcation['more']=moredict
	body['data'] =  notifcation
	body['to'] = notifcation_token
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization':'key='+SERVER_API_KEY}
	user_to_send = account.query(account.notifications_token == notifcation_token).get()
	if user_to_send.send_notfications == "1":
		conn.request('POST', '/gcm/send', json.dumps(body), headers)
		response = conn.getresponse()
		logging.info('%s Sent data:\n%s\nResponse Status: %s\nResponse msg: %s',TAG,str(body),response.status,response.read())
	else:
		logging.info("User is not subscribed to notifications")
def login_required(f):
	def wrapper(*args, **kw):
		TAG = "LOGIN_REQUIRED: "
		try:
			body = json.loads(args[0].body)
			user_in_db = ndb.Key('account', int(body['token'])).get()
			# logging.debug("%s%s",TAG,user_in_db.custom_to_dict)
		except:
			logging.error('%sReceived inappropriate request %s', TAG, str(args[0].body))
			return HttpResponseBadRequest()
		if not user_in_db: # Not a user !
			return HttpResponseForbidden()
		else:
			return f(*args, **kw)
	return wrapper




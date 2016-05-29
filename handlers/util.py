from constants import *
import json
import urllib2
import httplib
import constants
import logging
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
	conn.request('POST', '/gcm/send', json.dumps(body), headers)
	response = conn.getresponse()

	logging.info('%s Sent data:\n%s\nResponse Status: %s\nResponse msg: %s',TAG,str(body),response.status,response.read())

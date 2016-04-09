from constants import *
import json
import urllib2

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



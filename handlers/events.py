from entities import *
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from google.appengine.ext import ndb
from util import *
from django.views.decorators.csrf import csrf_exempt
from google.appengine.api import search
import datetime
import logging


@csrf_exempt
def create_event(request):
	TAG = 'CREATE_EVENT: '
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_name = body['event_name']
		event_type = body['event_type']
		event_date = body['event_date']
		event_location = body['event_location']
	except:

		return HttpResponseBadRequest()

	get_location = get_geoaddrees_by_coordinates(event_location['lon'],event_location['lat'])
	new_event = event(name=event_name,
	                  type=event_type,
	                  date=datetime.datetime.now(),
	                  location=ndb.GeoPt(event_location['lon'], event_location['lat']),
	                  members =[ndb.Key('account', int(token))],
	                  created_by = ndb.Key('account', int(token)),
	                  formatted_location = get_location
	                  )
	#
	new_event.put()
	return HttpResponse(create_response(OK, new_event.custom_to_dict()))

	# except:
	# 	return HttpResponseServerError()

@csrf_exempt
def get_all_events(request):
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
	except:
		return HttpResponseBadRequest()

	query_result = event.query().fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))

@csrf_exempt
def get_events_by_user(request):
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		user_id = body['user_id']
	except:
		return HttpResponseBadRequest()

	user_key = ndb.Key('account',int(user_id))
	query_result = event.query(event.members==user_key).fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))


@csrf_exempt
def join_event(request):
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		return HttpResponseBadRequest()
	event_to_update = ndb.Key('event',int(event_id)).get()
	event_to_update.members.append(ndb.Key('account',int(token)))
	event_to_update.put()
	return HttpResponse(create_response(OK, event_to_update.custom_to_dict()))


@csrf_exempt
def get_event(request):
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		return HttpResponseBadRequest()
	event_needed= ndb.Key('event',int(event_id)).get()
	return HttpResponse(create_response(OK, event_needed.custom_to_dict()))

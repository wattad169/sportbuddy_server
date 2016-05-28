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
		event_name = body['name']
		event_type = body['type']
		event_date = body['date']
		from_time = body['from_time']
		end_time = body['end_time']
		description = body['description']
		event_location = body['location']
		get_location = body['formatted_location']
		min_attend = body['minatt']
		max_attend = body['maxatt']

	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	# get_location = get_geoaddrees_by_coordinates(event_location['lon'],event_location['lat'])
	new_event = event(name=event_name,
	                  type=event_type,
	                  date=datetime.datetime.strptime(event_date, '%m/%d/%Y'),
	                  location=ndb.GeoPt(event_location['lat'], event_location['lon']),
	                  members =[ndb.Key('account', int(token))],
	                  created_by = ndb.Key('account', int(token)),
	                  formatted_location = get_location,
	                  from_time =from_time,
	                  end_time = end_time,
	                  description = description,
	                  min_attend = min_attend,
	                  max_attend = max_attend
	                  )
	#
	new_event.put()
	logging.info('%sEvent added %s',TAG,str(request.body))
	return HttpResponse(create_response(OK, [new_event.custom_to_dict()]))

	# except:
	# 	return HttpResponseServerError()

@csrf_exempt
def get_all_events(request):
	TAG = 'GET_ALL_EVENTS'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	query_result = event.query().fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))

@csrf_exempt
def get_events_by_user(request):
	TAG = 'GET_EVENT_BY_USER'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		user_id = body['user_id']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	user_key = ndb.Key('account',int(user_id))
	query_result = event.query(event.members==user_key).fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))


@csrf_exempt
def join_event(request):
	TAG = 'JOIN_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()
	# adding the user token to the given event
	event_to_update = ndb.Key('event',int(event_id)).get()
	event_to_update.members.append(ndb.Key('account',int(token)))
	event_to_update.put()
	# adding the event to the user events
	user_to_update = ndb.Key('account',int(token)).get()
	user_to_update.events.append(ndb.Key('event',int(event_id)))
	user_to_update.put()
	try:
		created_by_user = event_to_update.created_by.id()
		created_user= ndb.Key('account',int(created_by_user)).get()
		notification_token = created_user.notifications_token
		user_first_name = user_to_update.fullname[:user_to_update.fullname.find("%")]
		send_notifcation_to_user(notification_token,
		                         "{0} joined your event!".format(user_first_name),
		                         "Click here to approve",
		                         event_to_update.custom_to_dict())
	except Exception as e:
		logging.error('%sSending notifcation to user Failed %s',TAG,str(e))
	logging.info('%sUser %s joined event %s',TAG,token,event_id)
	return HttpResponse(create_response(OK, event_to_update.custom_to_dict()))


@csrf_exempt
def get_event(request):
	TAG = 'GET_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()
	event_needed= ndb.Key('event',int(event_id)).get()
	return HttpResponse(create_response(OK, event_needed.custom_to_dict()))


@csrf_exempt
def get_members_urls(request):
	# Example: {"token":"5660980839186432","event_id":"5764017373052928"}

	TAG = 'GET_MEMBERS_URLS'
	try:
		body = json.loads(request.body)
		result = {}
		url_list = []
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()
	event_in_db = ndb.Key('event',int(event_id)).get()
	event_members = event_in_db.members
	logging.info('%s Members_id %s',TAG,event_members)
	for event_member_key in event_members:
		event_member = ndb.Key('account',int(event_member_key.id())).get()
		url_list.append(event_member.photo_url)


	return HttpResponse(create_response(OK, url_list))
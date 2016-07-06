import logging

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb

from entities import *
from util import *


@csrf_exempt
def get_user_info(request):
	TAG = 'GET_USER_INFO'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		user_id = body['user_id']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	user_in_db = ndb.Key('account',int(user_id)).get()
	return HttpResponse(create_response(OK, user_in_db.custom_to_dict()))


@csrf_exempt
def register_for_notifications(request):
	TAG ='register_for_notifications'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		notifications_token = body['notifications_token']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	user_in_db = ndb.Key('account',int(token)).get()
	user_in_db.notifications_token = notifications_token
	user_in_db.put()
	return HttpResponse(create_response(OK, user_in_db.custom_to_dict()))

@csrf_exempt
def get_all_users(request):
	TAG ='get_all_users'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	query_result = account.query().fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))



@csrf_exempt
def invite_user_to_event(request):
	TAG = 'invite_user_to_event'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		invitee = body['invitee']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	inviter = ndb.Key('account', int(token)).get()
	invitee = ndb.Key('account', int(invitee)).get()
	event = ndb.Key('event', int(event_id)).get()
	invitee_first_name = inviter.fullname[:invitee.fullname.find("%")]
	send_notifcation_to_user(invitee.notifications_token,
	                         "{0} invited you to join {0}".format(invitee_first_name,event.name),
	                        "Click here to join the event!",
	                         event.custom_to_dict()
	                        )
	return HttpResponse(create_response(OK, []))


@csrf_exempt  # need to be checked
def get_user_by_photo(request):
	TAG = 'GET_USER_BY_PHOTO'
	try:
		body = json.loads(request.body)
		result = {}
		query_result = []
		token = body['token']
		photo_url = body['photo_url']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	query_result = account.query(account.photo_url == photo_url).fetch()
	return HttpResponse(create_response(OK, query_result[0].custom_to_dict()))

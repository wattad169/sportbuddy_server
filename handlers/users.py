from entities import *
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from google.appengine.ext import ndb
from util import *
from django.views.decorators.csrf import csrf_exempt
from google.appengine.api import search
import datetime
import logging


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
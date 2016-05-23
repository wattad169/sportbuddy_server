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
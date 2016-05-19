from django.http import HttpResponseForbidden,HttpResponseBadRequest,HttpResponse,HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb
from constants import *
from util import *
from entities import *
import logging

@csrf_exempt
def add_user(request):
	TAG = 'ADD_USER'
	try:
		body = json.loads(request.body)
		result = {}
		email = body['email']
		password = body['password']
		name = body['fullname']
		img = body['photo']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	# try:s

	query_result = account.query(account.email == email)
	if query_result.count() != 0:
		return HttpResponse(create_response(NOK, "This User Is Already Exists"))
	new_user = account(email = email ,password = str(hash(password)),fullname = name,photo_url = '',photo = str(img))
	new_user.put()
	id = new_user.key.id()
	logging.info('%sNew user added %s',TAG,str(request.body))
	return HttpResponse(create_response(OK, new_user.custom_to_dict()))
	# except :
	# 	return HttpResponseServerError()

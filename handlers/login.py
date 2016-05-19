# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONfDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.http import HttpResponseForbidden,HttpResponseBadRequest,HttpResponse,HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb
from util import *
from entities import *
import logging


@csrf_exempt
def login_from_client(request):
	auth = False
	TAG = "LOGIN"
	try:
		body = json.loads(request.body)
		result = {}
		mode = body['mode']
	except:
		return HttpResponseBadRequest()

	try:
		new_user = None
		if mode == LOGIN:
			email = body['email']
			password = body['password']
			query_result = account.query(ndb.AND(account.email == email, account.password == str(hash(password))))
			if query_result.count() !=0 : # Success
				auth = True
				new_user = query_result.get()
		elif mode == FACEBOOK_USER:
			auth = True
			fb_id = body['facebook_id']
			name = body['name']
			img = body['photo_url']
			query_result = account.query(ndb.AND(account.facebook_id == fb_id))
			if query_result.count() == 0: # Facebook user doesn't exist, create it and return user_id
				new_user = account(email = fb_id ,facebook_id = fb_id,fullname = name,photo_url = img,photo ='')
				new_user.put()
			else: # Facebook user registered, fetch id
				new_user = query_result.get()

		elif mode == GOOGLE_USER:
			auth = True
			email = body['email']
			name = body['name']
			img = body['photo_url']
			query_result = account.query(ndb.AND(account.google_id == email))
			if query_result.count() == 0:
				new_user = account(email = email , google_id = email,fullname = name,photo_url = img,photo ='')
				new_user.put()
			else: # Facebook user registered, fetch id
				new_user = query_result.get()
		else:
			logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
			return HttpResponseBadRequest()

		if(auth):
			logging.info('%sNew user logged in %s',TAG,str(request.body))
			return HttpResponse(create_response(OK, new_user.custom_to_dict()))
		else:
			return HttpResponse(create_response(NOK, result))
	except KeyError:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()
	except Exception as e:
		logging.error('%sError is server when request: %s exception %s',TAG,str(request.body),str(e))
		return HttpResponseServerError()



def generate_token(user_name):
	pass


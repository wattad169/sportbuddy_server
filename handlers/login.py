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


@csrf_exempt
def login_from_client(request):
	try:
		body = json.loads(request.body)
		result = {}
		user_name = body['user_name']
		password = body['password']
	except:
		return HttpResponseBadRequest()

	# if(user_name > 64 or password > 64):
	# 	return HttpResponseBadRequest()

	try:
		query_result = account.query(ndb.AND(account.username == user_name, account.password == str(hash(password))))
		if (query_result.count() == 0):
			return HttpResponse(create_response(NOK, result))
		else:
			user_exist = query_result.get()
			#result = generate_token(user_name)
			return HttpResponse(create_response(OK, user_exist.key.id()))
	except:
		return HttpResponseServerError()



def generate_token(user_name):
	pass


@csrf_exempt
def add_user(request):
	try:
		body = json.loads(request.body)
		result = {}
		user_name = body['user_name']
		password = body['password']
	except:
		return HttpResponseBadRequest()

	# if(user_name > 64 or password > 64):
	# 	return HttpResponseBadRequest()
	try:
		new_user = account(username = user_name , password = str(hash(password)))


		new_user.put()
		result = new_user.key.id()
		return HttpResponse(create_response(OK, result))

	except:
		return HttpResponseServerError()
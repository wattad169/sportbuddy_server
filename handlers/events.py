import datetime

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb

from entities import *
from util import *


@csrf_exempt
def create_event(request):  # Todo 7.7 update according to new DB : 1.is_public
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
		is_public = body['is_public']


	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()


	new_event = event(name=event_name,
	                  type=event_type,
	                  date=datetime.datetime.strptime(event_date, '%d-%m-%Y'),
	                  location=ndb.GeoPt(event_location['lat'], event_location['lon']),
	                  members =[ndb.Key('account', int(token))],
	                  created_by = ndb.Key('account', int(token)),
	                  formatted_location = get_location,
	                  from_time =from_time,
	                  end_time = end_time,
	                  description = description,
	                  min_attend = min_attend,
	                  max_attend = max_attend,
	                  is_public = str(is_public)
	                  )
	#
	event_key = new_event.put()
	# add the event to the user event
	user_entity = ndb.Key('account',int(token)).get()
	user_entity.events.append(event_key)
	user_entity.put()

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
def get_events_by_user(request):  #Todo 7.7 update according to new DB
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
def filter_events(request):
	TAG = 'FILTER_EVENTS'
	logging.error('%s1%s', TAG, str(request.body))
	try:
		body = json.loads(request.body)
		result = {}
		events_list = []
		token = body['token']
		date = body['date']
		type = body['type']
		distance = body['distance']
	except:
		logging.error('%s2 %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	logging.error('%s2.5 %s', TAG, str(request.body))

	events_list = event.query().fetch()
	if (date != ""):
		events_list = [event for event in events_list if str(event.date) == date]
		logging.error('%s3 %s', TAG, str(request.body))
	if (type != ""):
		events_list = [event for event in events_list if str(event.type) == type]
		logging.error('%s4 %s', TAG, str(request.body))
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in events_list]))


@csrf_exempt
def join_event(request):  #Todo 7.7 update according to new DB
	TAG = 'JOIN_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()

	# TODO:if  is_public ==0: #(need approval)
	# add user to the events_wait4aprroval
	# TNotification TO the creator
	# the notification move the userid from events_wait4aprroval to events_decline or events

	# if is is_public==1 (regular):

	# adding the user token to the given event
	event_to_update = ndb.Key('event',int(event_id)).get()
	event_to_update.members.append(ndb.Key('account',int(token)))
	event_to_update.put()
	# adding the event to the user events
	user_to_update = ndb.Key('account', int(token)).get()  #retrieve the relevant account entity
	user_to_update.events.append(ndb.Key('event',int(event_id)))
	user_to_update.put()

	###idan change temp###################
	###user_to_update.events_history.append(ndb.Key('event',int(event_id)))
	###user_to_update.put()
	#################################

	try:
		created_by_user = event_to_update.created_by.id()  # id of creator
		created_user = ndb.Key('account', int(created_by_user)).get()  # ta
		notification_token = created_user.notifications_token  #notification token
		user_first_name = user_to_update.fullname[:user_to_update.fullname.find("%")]
		send_notifcation_to_user(notification_token,  # send to
								 "{0} joined your event!".format(user_first_name),  # message
								 "Click here to approve",  # body
								 event_to_update.custom_to_dict())  #the tvent that if we click we get into
	except Exception as e:
		logging.error('%sSending notifcation to user Failed %s',TAG,str(e))
	logging.info('%sUser %s joined event %s',TAG,token,event_id)
	return HttpResponse(create_response(OK, event_to_update.custom_to_dict()))



@csrf_exempt
def leave_event(request):
	TAG = 'LEAVE_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']  # the token is the user_id
		event_id = body['event_id']
	except:
		logging.error('% sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	# remove the user token from the given event
	#check inwhich event Table the user in
	event_to_remove_from = ndb.Key('event', int(event_id)).get()
	# event_to_remove_from = ndb.Key('events_edited', int(event_id)).get() Todo : update
	# event_to_remove_from = ndb.Key('events_wait4approval', int(event_id)).get()
	#event_to_remove_from = ndb.Key('events_decline', int(event_id)).get()

	logging.info('event_to_remove_from = ' + str(event_to_remove_from))
	event_to_remove_from.members.remove(ndb.Key('account', int(token)))
	event_to_remove_from.put()  #
	# removing the event from the user events
	user_to_update = ndb.Key('account',int(token)).get()

	user_to_update.events.remove(ndb.Key('event', int(event_id)))  # remove2?
	user_to_update.put()  # put?

	logging.info('%s User %s leaved event %s', TAG, token, event_id)
	return HttpResponse(create_response(OK, event_to_remove_from.custom_to_dict()))


@csrf_exempt
def cancel_event(request):  # need to finish
	"""cancel all the event"""
	TAG = 'CANCEL_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']  # not relevant
		event_id = body['event_id']
	except:
		logging.error('%s Received inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	# remove the event from the DB
	event_to_cancel = ndb.Key('event', int(event_id)).get()
	logging.info('event_to_cancel = ' + str(event_to_cancel))
	event_to_cancel.key.delete();
	logging.info('made event_to_cancel.key.delete()\n' + 'event_to_cancel = ' + str(event_to_cancel))

	# removing the event from all users' events record - is it needed? No

	# TODO : FOR MOSTAFA: add here notification to inform that the event canceled.


	logging.info('%s  : %s', TAG, event_id)
	return HttpResponse(create_response(OK, event_to_cancel.custom_to_dict()))






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
	"""return url list """
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

@csrf_exempt
def update_event(request):
	TAG = 'EDIT_EVENT: '
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		new_event_name = body['name']
		new_event_type = body['type']
		new_event_date = body['date']
		new_from_time = body['from_time']
		new_end_time = body['end_time']
		new_description = body['description']
		new_event_location = body['location']
		new_get_location = body['formatted_location']
		new_min_attend = body['minatt']
		new_max_attend = body['maxatt']
		event_id  = body['event_id'] # event id that we need to update

	except:
		logging.error('%sReceived inappropriate request %s',TAG,str(request.body))
		return HttpResponseBadRequest()
	try:
		updated_event= ndb.Key('event',int(event_id)).get()
		updated_event.name = new_event_name
		updated_event.type = new_event_type
		updated_event.date = datetime.datetime.strptime(new_event_date, '%d-%m-%Y')
		updated_event.from_time = new_from_time
		updated_event.end_time = new_end_time
		updated_event.description = new_description
		updated_event.location=ndb.GeoPt(new_event_location['lat'], new_event_location['lon'])
		updated_event.formatted_location = new_get_location
		updated_event.min_attend = new_min_attend
		updated_event.max_attend = new_max_attend
		# I assume we are not allowing changing event public/private
		updated_event.put()
		# send notifcation to event members that the event has updated
		for event_member_key in updated_event.members:
			if int(event_member_key.id()) == token: # don't send notification to event updater
				continue
			event_member = ndb.Key('account',int(event_member_key.id())).get()
			send_notifcation_to_user(event_member.notifications_token,  # send to
								 "{0} has been updated!".format(updated_event.name),  # message
								 "Click here to view the event",  # body
								 updated_event.custom_to_dict())  #the tvent that if we click we get into
		logging.info('%sEvent Updated %s',TAG,str(request.body))
		return HttpResponse(create_response(OK, [updated_event.custom_to_dict()]))
	except Exception as e:
		logging.error('%s\n%s\nError:\n%s',TAG,str(request.body),e)



from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb

from entities import *
from util import *


@csrf_exempt
@login_required
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
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	new_event = event(name=event_name,
					  type=event_type,
					  date=datetime.datetime.strptime(event_date, '%d-%m-%Y'),
					  location=ndb.GeoPt(event_location['lat'], event_location['lon']),
					  members=[ndb.Key('account', int(token))],
					  created_by=ndb.Key('account', int(token)),
					  formatted_location=get_location,
					  from_time=from_time,
					  end_time=end_time,
					  description=description,
					  min_attend=min_attend,
					  max_attend=max_attend,
					  is_public=str(is_public)
					  )
	#
	event_key = new_event.put()
	# add the event to the user event -not working
	user_entity = ndb.Key('account', int(token)).get()
	user_entity.events.append(event_key)
	user_entity.created_count = str(int(user_entity.created_count) + 1)
	user_entity.put()

	logging.info('%sEvent added %s', TAG, str(request.body))
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
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	query_result = event.query(event.status != EXPIRED_EVENT).fetch()
	return HttpResponse(create_response(OK, [p.custom_to_dict() for p in query_result]))


@csrf_exempt
def get_events_by_user(request):  # Todo 7.7 update according to new DB
	TAG = 'GET_EVENT_BY_USER'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		user_id = body['user_id']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	user_key = ndb.Key('account', int(user_id))
	query_result = event.query(event.members == user_key).fetch()
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
@login_required
def join_event(request):
	TAG = 'JOIN_EVENT'
	try:
		body = json.loads(request.body)
		result = {}
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	event_to_update = ndb.Key('event', int(event_id)).get()
	user_to_update = ndb.Key('account', int(token)).get()  # retrieve the relevant account entity

	if event_to_update.members_count == int(event_to_update.max_attend):  # notify about closed event
		return HttpResponse(create_response(NOK, event_to_update.custom_to_dict()))

	created_by_user = event_to_update.created_by.id()
	created_user = ndb.Key('account', int(created_by_user)).get()
	notification_token = created_user.notifications_token
	user_first_name = user_to_update.fullname[:user_to_update.fullname.find("%")]
	send_notifcation_to_user(notification_token,
							 "{0} joined your event!".format(user_first_name),
							 "More details..",
							 event_to_update.custom_to_dict())
	if event_to_update.members_count == int(event_to_update.max_attend):  # notify about closed event
		send_notifcation_to_user(notification_token,
								 "{0} event is full!".format(event_to_update.name),
								 "",
								 event_to_update.custom_to_dict())

	if ndb.Key('account', int(token)) not in event_to_update.members:
		# adding the user token to the given event
		event_to_update.members.append(ndb.Key('account', int(token)))
		event_to_update.put()
	if ndb.Key('event', int(event_id)) not in user_to_update.events:
		# adding the event to the user events
		user_to_update.events.append(ndb.Key('event', int(event_id)))
		user_to_update.put()



	if event_to_update.members_count == int(event_to_update.max_attend):  # notify about closed event
		send_notifcation_to_user(notification_token,
								 "{0} event is full!".format(event_to_update.name),
								 "",
								 event_to_update.custom_to_dict())

	logging.info('%sUser %s joined event %s', TAG, token, event_id)
	return HttpResponse(create_response(OK, event_to_update.custom_to_dict()))


@csrf_exempt
@login_required
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
	# check inwhich event Table the user in
	event_to_remove_from = ndb.Key('event', int(event_id)).get()


	logging.info('event_to_remove_from = ' + str(event_to_remove_from))
	event_to_remove_from.members.remove(ndb.Key('account', int(token)))
	event_to_remove_from.put()  #
	# removing the event from the user events
	user_to_update = ndb.Key('account', int(token)).get()

	user_to_update.events.remove(ndb.Key('event', int(event_id)))  # remove2?
	user_to_update.put()  # put?

	created_by_user_id = event_to_remove_from.created_by.id()
	created_user = ndb.Key('account', int(created_by_user_id)).get()
	notification_token = created_user.notifications_token
	user_first_name = user_to_update.fullname[:user_to_update.fullname.find("%")]
	send_notifcation_to_user(notification_token,
							 "{0} left your event!".format(user_first_name),
							 "More details...",
							 event_to_remove_from.custom_to_dict())

	logging.info('%s User %s leaved event %s', TAG, token, event_id)
	return HttpResponse(create_response(OK, event_to_remove_from.custom_to_dict()))


@csrf_exempt
@login_required
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

	event_to_cancel = ndb.Key('event', int(event_id)).get()


	# send notifcation to event members that the event has canceled and delteing from member's event
	for event_member_key in event_to_cancel.members:
		event_member = ndb.Key('account', int(event_member_key.id())).get()

		needed_fields = [event_member.events,
						 event_member.events_wait4approval, event_member.events_decline]
		for user_field in needed_fields:
			key_temp = ndb.Key('event', int(event_id))
			if key_temp in user_field:
				idx = user_field.index(key_temp)
				user_field.pop(idx)
				event_member.put()
		if int(event_member_key.id()) == int(token):  # don't send notification to event canceler
			continue
		send_notifcation_to_user(event_member.notifications_token,  # send to
								 "{0} has been canceled!".format(event_to_cancel.name),  # message
								 "")

	# decrement created_count for the creator
	user_entity = ndb.Key('account', int(token)).get()
	user_entity.created_count = str(int(user_entity.created_count) - 1)
	user_entity.put()

	# remove the event from the DB
	logging.info('event_to_cancel = ' + str(event_to_cancel))
	event_to_cancel.key.delete()

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
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	event_needed = ndb.Key('event', int(event_id)).get()
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
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	event_in_db = ndb.Key('event', int(event_id)).get()
	event_members = event_in_db.members
	logging.info('%s Members_id %s', TAG, event_members)
	for event_member_key in event_members:
		event_member = ndb.Key('account', int(event_member_key.id())).get()
		url_list.append(event_member.photo_url)

	return HttpResponse(create_response(OK, url_list))


@csrf_exempt
@login_required
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
		event_id = body['event_id']  # event id that we need to update

	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()
	try:
		updated_event = ndb.Key('event', int(event_id)).get()
		updated_event.name = new_event_name
		updated_event.type = new_event_type
		updated_event.date = datetime.datetime.strptime(new_event_date, '%d-%m-%Y')
		updated_event.from_time = new_from_time
		updated_event.end_time = new_end_time
		updated_event.description = new_description
		updated_event.location = ndb.GeoPt(new_event_location['lat'], new_event_location['lon'])
		updated_event.formatted_location = new_get_location
		updated_event.min_attend = new_min_attend
		updated_event.max_attend = new_max_attend
		# I assume we are not allowing changing event public/private
		updated_event.put()
		# send notifcation to event members that the event has updated
		for event_member_key in updated_event.members:
			if int(event_member_key.id()) == int(token):  # don't send notification to event updater
				continue
			event_member = ndb.Key('account', int(event_member_key.id())).get()
			send_notifcation_to_user(event_member.notifications_token,  # send to
									 "{0} has been updated!".format(updated_event.name),  # message
									 "More details...",  # body
									 updated_event.custom_to_dict())  # the tvent that if we click we get into
		logging.info('%sEvent Updated %s', TAG, str(request.body))
		return HttpResponse(create_response(OK, [updated_event.custom_to_dict()]))
	except Exception as e:
		logging.error('%s\n%s\nError:\n%s', TAG, str(request.body), e)

@csrf_exempt
@login_required
def request_join_event(request):
	TAG = 'EDIT_EVENT:'
	try:
		body = json.loads(request.body)
		token = body['token']
		event_id = body['event_id']
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))
		return HttpResponseBadRequest()

	event_key = ndb.Key('event', int(event_id))
	user_key = ndb.Key('account', int(token))
	event_to_update = event_key.get()
	user_to_update = user_key.get()

	# add event to the waiting_for_approve in under the user
	if event_key not in user_to_update.events_wait4approval:
		user_to_update.events_wait4approval.append(event_key)

	# add to the event approve list
	if user_key not in event_to_update.approve_list:
		event_to_update.approve_list.append(user_key)

	user_to_update.put()
	event_to_update.put()

	# send join request to the event boss
	created_by_user_id = event_to_update.created_by.id()
	created_user = ndb.Key('account', int(created_by_user_id)).get()
	notification_token = created_user.notifications_token
	user_first_name = user_to_update.fullname[:user_to_update.fullname.find("%")]
	send_notifcation_to_user(notification_token,
							 "{0} requested to join your event!".format(user_first_name),
							 "",
							 event_to_update.custom_to_dict())

	return HttpResponse(create_response(OK, []))

@csrf_exempt
@login_required
def resolve_join_request_response(request):
	TAG = 'RESOLVE_JOIN_REQUEST_RESPONSE: '
	try:
		body = json.loads(request.body)
		token       = body['token']
		user_id     = body['user_id']
		event_id    = body['event_id']
		join_status = int(body['join_status'])
	except:
		logging.error('%sReceived inappropriate request %s', TAG, str(request.body))

	event_key = ndb.Key('event', int(event_id))
	user_key = ndb.Key('account', int(user_id))
	user_to_update = user_key.get()
	event_to_update = event_key.get()
	notification_token = user_to_update.notifications_token

	# remove from sender approve list
	event_approve_list = event_to_update.approve_list
	if user_key in event_approve_list:
		logging.debug("in removing from approve list")
		idx = event_approve_list.index(user_key)
		event_approve_list.pop(idx)

	# delete from wait4approval list
	user_event_list = user_to_update.events_wait4approval
	if event_key in user_event_list:
		logging.debug("in removing from events_wait4approval")
		idx = user_event_list.index(event_key)
		user_to_update.events_wait4approval.pop(idx)
	if join_status:
		# add to user events
		if event_key not in user_to_update.events:
			logging.debug("in adding to events")
			user_to_update.events.append(event_key)
		# add to event members
		if user_key not in event_to_update.members:
			event_to_update.members.append(user_key)
		event_to_update.put()
		user_to_update.put()
		send_notifcation_to_user(notification_token,
							 "Your join request has been accepted",
							 "See event details.",
							 event_to_update.custom_to_dict())
	else:
		# add to user declined events list
		if event_key not in user_to_update.events_decline:
			logging.debug("in adding to events")
			user_to_update.events_decline.append(event_key)
		event_to_update.put()
		user_to_update.put()
		send_notifcation_to_user(notification_token,
							 "Your join request has been declined",
							 "",
							 event_to_update.custom_to_dict())



	return HttpResponse(create_response(OK, []))
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import ndb
import datetime
from entities import *
from util import *
from constants import *

@csrf_exempt
def event_refresher(request):
	'''
	refresh the events every 1 minute to and updates events status by state (expired/live)
	:param request:
	:return:
	'''
	TAG = 'EVENT_REFRESHER: '
	resolve_expired_events()
	resolve_live_events()
	return HttpResponse(create_response(OK, []))


def resolve_expired_events():
	TAG = 'UPDATE_EVENT_STATUS: '
	now_time = datetime.datetime.now()
	filtered_events = event.query(event.status == LIVE_EVENT,event.expire_date < now_time)
	filtered_cnt = filtered_events.count()
	filtered_events_result = filtered_events.fetch()
	for iter_event in filtered_events_result:
		iter_event.status = EXPIRED_EVENT
		iter_event.put()
	logging.debug('%s%s expired events has been resolved',TAG,filtered_cnt)

def resolve_live_events():
	TAG = 'UPDATE_EVENT_STATUS: '
	now_time = datetime.datetime.now()
	filtered_events = event.query(ndb.AND(event.status == OPEN_EVENT,
	                                      event.start_date < now_time )) # now game is on
	filtered_cnt = filtered_events.count()
	filtered_events_result = filtered_events.fetch()
	for iter_event in filtered_events_result:
		if iter_event.expire_date > now_time:
			iter_event.status = LIVE_EVENT
			iter_event.put()


	logging.debug('%s%s live events has been resolved',TAG,filtered_cnt)

@csrf_exempt
def resolve_kick_of_events(request):
	'''
	notify the user one hour before the kick off
	:return:
	'''
	TAG = 'UPDATE_EVENT_STATUS: '
	now_time = datetime.datetime.now()
	filtered_events = event.query(ndb.AND(event.status == OPEN_EVENT,
	                                      event.start_date < now_time + datetime.timedelta(hours=1))) # less than hour to start
	filtered_cnt = filtered_events.count()
	filtered_events_result = filtered_events.fetch()
	for iter_event in filtered_events_result:
		for event_member_key in iter_event.members:
			event_member = ndb.Key('account',int(event_member_key.id())).get()
			try:
				if iter_event.members_count < int(iter_event.min_attend):  # notify about closed event
					notify_str = "Your event didn't reach minimum required attendance!"
				else:
					notify_str = "Less than an hour til we kick off!"

				send_notifcation_to_user(event_member.notifications_token,
											 notify_str,
											 "",
											 iter_event.custom_to_dict())
			except Exception as e:
				logging.debug("trying to send notification to user {0} failed\nExcetpions:\n{1}".format(int(event_member_key.id()),e))
				continue
	logging.debug('%s%s kick off events has been resolved',TAG,filtered_cnt)
	return HttpResponse(create_response(OK, []))



@csrf_exempt
def update_events_by_scheme(request):
	TAG = 'UPDATE_ALL_BY_SCHEME'
	all_events = event.query().fetch()
	for iter_event in all_events:
		iter_event.put()
	return HttpResponse(create_response(OK, []))


@csrf_exempt
def update_users_by_scheme(request):
	TAG = 'UPDATE_ALL_BY_SCHEME'
	all_users = account.query().fetch()
	for iter_user in all_users:
		iter_user.put()
	return HttpResponse(create_response(OK, []))
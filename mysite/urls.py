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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import include, url
from django.contrib import admin
from handlers.login import *
from handlers.events import *
from handlers.register import *
from handlers.users import *



urlpatterns = [
	# url(r'^$', index),
	# url(r'^admin/', include(admin.site.urls)),
	# url(r'^testest/', index_test),
	url(r'^login/', login_from_client),
	url(r'^register/', add_user),
	url(r'^create_event/', create_event),
	url(r'^get_all_events/', get_all_events),
	url(r'^get_events_by_user/', get_events_by_user),
	url(r'^join_event/', join_event),
	url(r'^get_event/', get_event),
	url(r'^get_members_urls/',get_members_urls),
	url(r'^get_user_info/',get_user_info),
	url(r'^register_for_notifications/',register_for_notifications),
	url(r'^get_all_users/',get_all_users),
	url(r'^invite_user_to_event',invite_user_to_event)
]

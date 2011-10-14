"""
 urls.py - URL routing for GoldRush Microservices django app
"""
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
#
# Copyright: 2011 Colorado College
__author__ = 'Jeremy Nelson'

from django.conf.urls.defaults import *

urlpatterns = patterns('grx.views',
    url(r'^$','default',name='grx-index'),
    url(r'search$','search',name='grx-search'),
    url(r'subjects$','subjects',name='grx-subjects'),
    url(r'subject/(.*)$','subjects',name='grx-subject'),
    url(r'titles$','titles',name='grx-titles'),
    url(r'titles/(.*)$','titles',name='grx-title'),
)


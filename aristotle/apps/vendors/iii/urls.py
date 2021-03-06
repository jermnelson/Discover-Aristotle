"""
 urls.py - URL routing for III Utilities django app
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

urlpatterns = patterns('vendors.iii.views',
    url(r'^$','index',name='iii-index'),
    url(r'csv$','csv',name='iii-csv'),
    url(r'patron_login$','patron_login',name='iii-login'),

)


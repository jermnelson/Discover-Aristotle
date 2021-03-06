"""
 urls.py - URL routing for MARC record utilities django app
"""
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
#
# Copyright: 2011 Colorado College
#
__author__ = 'Jeremy Nelson'
import marc.views
from django.conf.urls.defaults import *

urlpatterns = patterns('marc.views',
    url(r'^$','default',name='marc-index'),
    (r'process$','process'),
    url(r'search$','search',name='marc-search'),
    url(r'download$','download',name='marc-download'),
    url(r'update$','update_log',name='marc-update'),
    (r'(\w+)','record_load'),
#    (r'/success$','success'),
#    (r'(\w+)/upload','upload'),
)

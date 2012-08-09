# Copyright 2007 Casey Durfee
# Copyright 2007 Gabriel Farrell
#
# This file is part of Kochief.
# 
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
from discovery.feeds import SavedRecordsFeed

urlpatterns = patterns('discovery.views',
    url(r'^$', 'index', name='discovery-index'),
    url(r'^record/(.+)/refworks','refworks_item',name='discovery-record-refworks'),
    url(r'^record/(.+)$', 'record', name='discovery-record'),
    url(r'^search$', 'search', name='discovery-search'),
    url(r'^unapi$', 'unapi', name='discovery-unapi'),
    url(r'^advanced$','advanced_search', name='discovery-adv-search'),
    url(r'^cart$','get_cart', name='discovery-getcart'),
    url(r'^cart/add$','add_item_cart', name='discovery-add-item-cart'),
    url(r'^cart/drop$','drop_item_cart', name='discovery-drop-item-cart'),
    url(r'^cart/email$','email_cart', name='discovery-email-cart'),
    url(r'^cart/feed$',SavedRecordsFeed(),name='discovery-feed-cart'),
    url(r'^cart/print$','print_cart', name="discovery-print-cart"),
    url(r'^cart/refworks$','refworks_cart', name="discovery-print-cart"),
    url(r'^ajax/items$','get_all_items',name='all-record-items-dlg-body'),
    #(r'^feed/atom/$', 'atomFeed'),
    #(r'^feed/rss/$', 'rssFeed'),
)

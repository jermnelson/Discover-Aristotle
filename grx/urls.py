"""
 urls.py - URL routing for GoldRush Microservices django app

 2011 (c) - Colorado College
"""
__author__ = 'Jeremy Nelson'

from django.conf.urls.defaults import *

urlpatterns = patterns('grx.views',
    (r'^$','default'),
    (r'facet.json$','top_facets'),
    (r'subjects$','subjects'),
    (r'subjects/(\w+[\s\w]*)$','subjects'),
#    (r'rpc$','grx.rpc.rpc_handler'),
    (r'titles$','titles'),
    (r'titles/(\w+[\s\w]*)$','titles'),
)


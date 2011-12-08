"""
 :mod:`repository.urls` - URL routing for Aristotle Fedora Repository utilities
"""
__author__ = 'Jeremy Nelson'
import repository.views
from django.conf.urls.defaults import *

urlpatterns = patterns('repository.views',
    url(r'^$','default',name='repository-index'),
    url(r'mover$','object_mover',name='repository-mover'),
)

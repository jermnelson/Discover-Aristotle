"""
  refworks_extras.py - Contains Template Filters for creating an RefWorks URL 
  following suggestions at the `RefWorks Website <http://www.refworks.com/DirectExport.htm>`_
"""
#
#
#
# Copyright 2011 Colorado College
#
__author__ = 'Jeremy Nelson'

from django import template
from django.utils.safestring import mark_safe
from aristotle import settings as project_settings
import localsettings as settings

register = template.Library()

def get_refworks_url(database=None):
    """Function creates a hyper-link for importing a reference to RefWorks
    If REFWORKS URL is present in localsetting, takes precident over any
    REFWORKS_URL setting elsewhere in the app.
    """
    if settings.REFWORKS_URL:
        refworks_base = settings.REFWORKS_URL
    elif project_settings.REFWORKS_URL:
        refworks_base = project_settings.REFWORKS_URL
    else:
        raise ValueError('Cannot find REFWORKS_URL in either global or local'\
                         ' app settings')
    if 
    return mark_safe(refworks_url)

register.filter('get_refworks_url',
                get_refworks_url)

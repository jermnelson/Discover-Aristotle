"""
 marc_extras.py -- Template tags and filters for MARC utilities application
"""

__author__ = 'Jeremy Nelson'
import re,logging
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def get_bot_name(bot):
    """Method takes a Bot class and returns the name of the class because
    Django templates cannot call underscore methods or properties.
    """
    if type(bot) == str:
        return ''
    return mark_safe(bot.__name__)


register.filter('get_bot_name',get_bot_name)

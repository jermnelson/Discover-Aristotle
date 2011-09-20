# 
# grx_extras.py -- Custom Django template tags
#
# 
__author__ = 'Jeremy Nelson'
import urllib2,logging,urlparse
from django import template
import django.utils.simplejson as json
from django.utils.safestring import mark_safe

register = template.Library()


def get_favicon(url):
    """Function takes a url, parses out the root and attempts to
    retrieve the favicon and returns the url if not a 404"""
    url_object = urlparse.urlparse(url)
    favicon_url = 'http://%s/favicon.ico' % url_object.netloc
    try:
        url_result = urllib2.urlopen(favicon_url)
        if url_result.code != 200:
            return ''
        else:
            return mark_safe('<img src="%s" />' % favicon_url)
    except:
        return ''

def get_department(workflow):
    """Function takes workflow CONFIG object and returns
    the department name if present"""
    if workflow.has_option('FORM','department'):
        return mark_safe(workflow.get('FORM','department'))
    else:
        return ''  

register.filter('get_favicon',
                get_favicon)



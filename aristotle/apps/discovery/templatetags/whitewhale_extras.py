"""
  whitewhale_extras.py -- Template filters for generating a cached view of
  dynamic Colorado College website.
"""
__author__ = 'Jeremy Nelson'

import urllib2,logging
from django.core.cache import cache
from django import template
from django.utils.safestring import mark_safe
import lxml.html,lxml.etree
from discovery.config import CC_URL


register = template.Library()


def get_header():
    """Function returns cached version of header element from live CC site
    """
    header = cache.get('cc-header')
    if header:
        return mark_safe(header)
    else:
        harvest_latest()
        return mark_safe(cache.get('cc-header'))

def harvest_latest():
    """Function retrieves latest snapshot from live CC site, uses xpath to 
    save portions of the site to cache."""
    try:
        cc_home = urllib2.urlopen(CC_URL)
    except HTTPError, e:
        logging.error("Unable to open CC_URL of %s" % CC_URL)
    cc_tree = lxml.html(cc_home)
    cc_tree.make_links_absolute(CC_URL)
    header = cc_tree.xpath('//div/header[@id="header"]')[0]
    cache.set('cc-header',lxml.etree.tostring(header))
    logging.error("CACHE is %s" % cache.get('cc-header'))
    
register.filter('get_header',get_header)
    
    
    

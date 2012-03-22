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


def get_footer(cache_key='cc-footer'):
    """Function returns cached version of footer element from live CC site

    :param cache_key: Key to retrieve footer from cache, defaults to 
                      cc-footer
    """
    footer = cache.get(cache_key)
    if footer:
        return mark_safe(footer)
    else:
        harvest_latest()
        return mark_safe(cache.get(cache_key))

def get_header(cache_key='cc-header'):
    """Function returns cached version of header element from live CC site

    :param cache_key: Key to retrieve header from cache, defaults to 
                      cc-header
    """
    header = cache.get(cache_key)
    if header:
        return mark_safe(header)
    else:
        harvest_latest()
        return mark_safe(cache.get(cache_key))

def get_tabs(cache_key='cc-tabs'):
    """Function returns cached version of library-tabs div element from 
    live CC site

    :param cache_key: Key to retrieve tabs from cache, defaults to 
                      cc-tabs
    """
    tabs = cache.get(cache_key)
    if tabs:
        return mark_safe(tabs)
    else:
        harvest_latest()
        return mark_safe(cache.get(cache_key))

def harvest_latest():
    """Function retrieves latest snapshot from live CC site, uses xpath to 
    save portions of the site to cache."""
    try:
        cc_home = urllib2.urlopen(CC_URL).read()
    except urllib2.HTTPError, e:
        logging.error("Unable to open CC_URL of %s" % CC_URL)
    cc_tree = lxml.html.document_fromstring(cc_home)
    cc_tree.make_links_absolute(CC_URL)
    header = cc_tree.xpath('//div/header[@id="header"]')[0]
    cache.set('cc-header',lxml.etree.tostring(header))
    footer = cc_tree.xpath('//footer[@id="footer"]')[0]
    cache.set('cc-footer',lxml.etree.tostring(footer))
    tabs = cc_tree.xpath('//div[@id="library-tabs"]')[0]
    cache.set('cc-tabs',lxml.etree.tostring(tabs,encoding='ISO-8859-15'))
    
register.filter('get_footer',get_footer)    
register.filter('get_header',get_header)
register.filter('get_tabs',get_tabs)
    
    

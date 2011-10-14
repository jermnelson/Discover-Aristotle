# 
# grx_extras.py -- Custom Django template tags
#
# 
__author__ = 'Jeremy Nelson'
import urllib2,logging,urlparse
from django import template
import django.utils.simplejson as json
from django.utils.safestring import mark_safe
import lxml.html 
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

def _create_row(**kwargs):
    """Internal function creates a table row with one th and
    one td child elements with provided values."""
    row = lxml.html.Element('tr')
    th = lxml.html.Element('th')
    td = lxml.html.Element('td')
    if kwargs.has_key('th'):
        th_content = kwargs.get('th')
        try: 
            th.append(th_content)
        except TypeError, e:
            th.text = th_content
    if kwargs.has_key('td'):
        td_content = kwargs.get('td')
        try:
            td.append(td_content)
        except TypeError, e:
            td.text = td_content
    row.append(th)
    row.append(td)
    return row

def generate_detail(resource_record,tr_class=None):
    """Function takes an GoldRush resource_record and generates a 
    and returns a table to the calling template"""
    tbody = lxml.html.Element('tbody')
    title_row = lxml.html.Element('tr')
    if tr_class:
        title_row.attrib['class'] = tr_class
    title = lxml.html.Element('a',href=resource_record.url)
    title.text = resource_record.dbname
    title_th = lxml.html.Element('th')
    title_th.append(title)
    title_row.append(title_th)
    start_td = lxml.html.Element('td')
    if resource_record.start:
        start_td.text = resource_record.start
        title_row.append(start_td)
        to_td = lxml.html.Element('td')
        to_td.text = 'to'
        title_row.append(to_td)
    if resource_record.end:
        end_td = lxml.html.Element('td')
        end_td.text = resource_record.end
        title_row.append(end_td)
    tbody.append(title_row)
    return mark_safe(lxml.html.tostring(tbody))

    

register.filter('get_favicon',
                get_favicon)
register.filter('generate_detail',
                generate_detail)

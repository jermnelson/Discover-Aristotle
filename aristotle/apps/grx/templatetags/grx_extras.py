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

def generate_detail(resource_record):
    """Function takes an GoldRush resource_record and generates a 
    and returns a table to the calling template"""
    tbody = lxml.html.Element('tbody')
    title = lxml.html.Element('a',href=resource_record.url)
    title.text = resource_record.dbname
    title_th = lxml.html.Element('th',colspan='2')
    title_th.append(title)
    title_row = lxml.html.Element('tr')
    title_row.append(title_th)
    tbody.append(title_row)
    provider_td = lxml.html.Element('td',colspan='2')
    provider_td.text = 'Provided by %s' % resource_record.provider
    provider_row = lxml.html.Element('tr')
    provider_row.append(provider_td)
    tbody.append(provider_row)
    if resource_record.start:
        tbody.append(_create_row(th='Start',td=resource_record.start))
    if resource_record.end:
        tbody.append(_create_row(th='End',td=resource_record.end))
    if resource_record.date_embargo:
        tbody.append(_create_row(th='Date Embargo',td=resource_record.date_embargo))
    if resource_record.date_notes or resource_record.grit_msg:
        notes = ''
        if resource_record.date_notes:
            notes = resource_record.date_notes
        if resource_record.grit_msg:
            if len(notes) > 1:
                notes += '<br/>'
            notes += resource_record.grit_msg
        tbody.append(_create_row(th='Notes',td=notes))
    table = lxml.html.Element('table')
    table.attrib['class'] = 'grx'
    table.append(tbody)
    return mark_safe(lxml.html.tostring(table))

    

register.filter('get_favicon',
                get_favicon)
register.filter('generate_detail',
                generate_detail)

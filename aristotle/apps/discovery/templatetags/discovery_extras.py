# Copyright 2008 Gabriel Sean Farrell
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

import urllib

from django.template import Library
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
import settings
from vendors.iii.bots.iiibots import ItemBot
import vendors.iii.settings as ils_settings

register = Library()

def title_link(context):
    new_context = {}
    new_context['record_url'] = context['doc']['record_url']
    try:
        full_title = context['doc']['full_title']
    except KeyError:
        full_title = _('Untitled')
    try:
        short_title = context['doc']['title']
    except KeyError:
        short_title = full_title
    new_context['short_title'] = short_title
    rest_of_title = full_title.replace(short_title, '', 1)
    new_context['rest_of_title'] = rest_of_title
    return new_context
register.inclusion_tag('discovery/snippets/result_title.html', 
        takes_context=True)(title_link)

def add_sort(context, sort_type):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    if limits_param:
        params.append(('limits', limits_param.encode('utf8')))
    params.append(('sort', sort_type.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(add_sort)

def pagination_url(context, page):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    if limits_param:
        params.append(('limits', limits_param.encode('utf8')))
    params.append(('sort', context['current_sort'].encode('utf8')))
    if page != 1:
        params.append(('page', page))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(pagination_url)

def new_limit(context, field, field_query):
    params = []
    limit = u'%s:"%s"' % (field, field_query)
    params.append(('limits', limit.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(new_limit)

def new_limit_raw(context, limit):
    params = []
    params.append(('limits', limit.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(new_limit_raw)

def add_limit(context, field, field_query):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    limit = u'%s:"%s"' % (field, field_query)
    limits = ' '.join((limits_param, limit))
    params.append(('limits', limits.encode('utf8')))
    params.append(('sort', context['current_sort'].encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(add_limit)

def remove_limit(context):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    current_limits = context['limits']
    this_limit = context['limit']
    limits = ' '.join([x for x in current_limits if x != this_limit])
    if limits:
        params.append(('limits', limits.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(remove_limit)

def display_ill(record):
    """Displays an ill and Hold links if the item's status is Checked out
    """
    ils_numbers = record.get('items')
    if not ils_numbers:
        ils_numbers = []
    for item_id in ils_numbers:
        item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
        status = item_bot.status()
        if status is not None:
            if item_bot.status().startswith('Due'):
                return mark_safe('''<li><a href="#" onclick="alert('ill tbd')">Request</a> <em>%s</em> through
   Prospector or Interlibrary Loan (ILL)</li>
  <li><a href="#" onclick="alert('hold tbd')">Hold</a> this item so that you can pick it up after the current borrower 
  is finished</li>''' % record.get('title'))
    return ''


def display_online(record):
    """Displays online access link if item's is available online
    """
    if record.has_key('url'):
        return mark_safe('''<li>Access <em><a href="%s">%s</a></em> online</li>''' % (record.get('url')[0],
                                                                                      record.get('title')))
    else:
        return ''


def get_cover_image(num_isbn):
    """Custom method queries multiple web services for a thumbnail image,
    returns a matched URL using isbn number
    """
    amazon_image_url = 'http://ec2.images-amazon.com/images/P/%s.01._PE00_SCMZZZZZZZ_.jpg' % num_isbn
    return mark_safe(amazon_image_url)

def get_item_status(item_id):
    """Method connects to ILS and retrieves the current circulation status
    of a an item.
    """
    item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
    item_status = item_bot.status()
    if item_status is None:
        css_class = ''
    elif item_status.startswith('Due'):
        css_class = 'due-back'
    else:
        css_class = 'available'
    status_txt = '''<span class="%s">%s''' % (css_class,item_status)
    volume = item_bot.volume()
    if volume:
        status_txt += item_bot.volume()
    status_txt += '</span>'
    location = item_bot.location()
    if location is not None:
        if not location.startswith('Online'):
            status_txt += ' located at %s' % location
    return mark_safe(status_txt) 

def get_marc_as_list(raw_marc):
    """Method takes Solr MARC format and splits into a list of field dictionarys
    """
    output = []
    marc_listing = raw_marc.split("=")
    for row in marc_listing:
        output.append({'tag':row[0:3],
                      'value':row[3:]})
    return output
  

def generate_prospector_url(record_id):
    """Generates link to Prospector's union catalog
    """
    prospector_url = settings.PROSPECTOR_URL % (record_id,record_id)
    return mark_safe(prospector_url)

def reduce_subjects(doc):
    """Iterates and sort all topic and subject related fields and
    returns a set of unique subjects.
    """
    subjects = []
    if doc.has_key('subject'):
        for subject in doc['subject']:
            subjects.append(subject)
    if doc.has_key('topic'):
        for topic in doc.get('topic'):
            subjects.append(topic)
    subjects.sort()
    return set(subjects)

def search_field_options(output_html):
    """
    Generates a list of field search options
    """
    field_types = [('keyword','Any Field'),
                   ('author','Author'),
                   ('title','Title'),
                   ('subject','Subject')]
    for row in field_types:
        output_html += '<option value="%s">%s</option>' % row
    return mark_safe(output_html)

def search_operator_options(output_html):
    """Generates a list of boolean search HTML options for
    AND, AND NOT, OR
    """
    for row in ['AND','AND NOT','OR']:
        output_html += '<option value="%s">%s</option>' % (row,row.title())
    return mark_safe(output_html)

register.filter('display_ill',display_ill)
register.filter('display_online',display_online)
register.filter('get_cover_image',get_cover_image) 
register.filter('get_item_status',get_item_status)
register.filter('get_marc_as_list',get_marc_as_list)
register.filter('generate_prospector_url',generate_prospector_url)
register.filter('reduce_subjects',reduce_subjects)
register.filter('search_field_options',search_field_options)
register.filter('search_operator_options',search_operator_options)

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

import urllib,urllib2
import sunburnt

from django.template import Context,Library,Template,loader
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.utils.safestring import mark_safe
import settings
from discovery.config import FORMAT_ICONS
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
    """
    Method adds sort to query stored in the context.

    :param context: Context object
    :param sort_type: Sort type
    :rtype: dictionary of urlparams
    """
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
    """
    Function creates a new limit

    :param context: Context
    :param field: Field for the new limit
    :param field_query: Query string to add limit
    :rtype: dictionary of urlparams
    """
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

def display_empty_facets(output_html):
    """Displays an empty list of facets for when query returns no hits

    :param output_html: HTML string
    :rtype string:
    """
    for facet in settings.FACETS:
        output_html += '<a href="#" onclick="DisplayFacet(this)">'
        output_html += '<h5 class="closed">%s</h5></a>' % facet['name']
        output_html += '<ul class="closed"><li>None</li></ul>'
    return mark_safe(output_html)
    

def display_ill(record):
    """Displays an ill and Hold links if the item's status is Checked out

    :param record: Solr response for a single document
    :rtype string:
    """
    ils_numbers = record.get('item_ids')
    ill_template = loader.get_template('ill_link_li.html')
    if not ils_numbers:
        ils_numbers = []
    for item_id in ils_numbers:
        item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
        status = item_bot.status()
        if status is not None:
            if item_bot.status().startswith('Due'):
                hold_link = settings.ILS_HOLD_URL % (3*(record.get('id'),))
                ill_link = generate_prospector_url(record.get('id'))
                context = Context({'hold_link':hold_link,
                                   'ill_link':ill_link,
                                   'title':record.get('title')})
                return mark_safe(ill_template.render(context))
    return ''


def display_online(record):
    """Displays online access link if item's is available online

    :param record: Solr document, required
    :rtype: String
    """
    if record.has_key('url'):
        return mark_safe('''<li>Access <em><a href="%s">%s</a></em> online</li>''' % (record.get('url')[0],
                                                                                      record.get('title')))
    else:
        return ''

class spellcheck_stub(object):
    """
    Spellcheck stub class for normalizing XML Solr Spellcheck with 
    Sunburnt SolrSpellCheck class
    """
    missspelledTerm = None
    suggestions = []

def display_spellcheck(spellcheck):
    """Displays Solr spellcheck results.

    :param spellcheck: Solr spellcheck, either Kochief Solr or Sunburnt 
                       Spellcheck object
    :rtype: String
    """
    spellcheck_template = loader.get_template('spellcheck.html')
    params = {}
    if type(spellcheck) == sunburnt.schema.SolrSpellCheck:
        params['spellcheck'] = spellcheck
    # Uses old manual Kochief-style SolrSpell check
    else:
        spell_stub = spellcheck_stub()
        if not spellcheck['suggestions'][0][1]: # correctly spelled is False
            spell_stub.missspelledTerm = spellcheck['suggestions'][0][0]
            for row in spellcheck['suggestions'][0][1]['suggestion']:
                spell_stub.suggestions.append(row)
        else:
            spell_stub.missspelledTerm = "NOT FOUND" # need to extract query term
        params['spellcheck'] = spell_stub
    context = Context(params)
    return mark_safe(spellcheck_template.render(context))

def get_adjacent(call_number,position):
    """Method queries Solr index for adjacent call number depending
    on position from current call number
   
    :param call_number: call number of current item
    :param position: position to retrieve adjacent item, negative is before call number,
                     positive is after call number
    """
    return mark_safe('')

def get_cover_image(num_isbn):
    """Custom method queries multiple web services for a thumbnail image,
    returns a matched URL using isbn number

    :param num_isbn: numeric string for an ISBN number, required
    :rtype: URL of Amazon cover image
    """
    amazon_image_url = 'http://ec2.images-amazon.com/images/P/%s.01._PE00_SCMZZZZZZZ_.jpg' % num_isbn
    return mark_safe(amazon_image_url)

def get_format_icon(term):
    """Custom method returns an img tag with URL to bundled Pinax Silk icon
    set.

    :param term: Term of format
    :rtype: String with URL to image 
    """
    if FORMAT_ICONS.has_key(term):
        return mark_safe(FORMAT_ICONS[term])
    else:
        return ''
   
def get_google_book(num_isbn):
    """Custom method queries Google Books API to retrieve urls and book 
    cover thumbnails to display to the end user.

    :param num_isbn: numeric string for an ISBN number, required
    :rtype: String of embedded HTML for Google Book cover
    """
    google_book_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s' % num_isbn
    try:
        book_json = simplejson.load(urllib2.urlopen(google_book_url))
    except:
        book_json = {'totalItems':0}
    if book_json["totalItems"] > 0:
        top_result = book_json["items"][0]
        output = '<div class="gbsLinkCover">'
        output += '''<a href="%s">''' % top_result["volumeInfo"]["infoLink"]
        if top_result['volumeInfo'].has_key('imageLinks'):
            output += '''<img src="%s" title="%s" />''' % \
                      (top_result['volumeInfo']['imageLinks']['smallThumbnail'],
                       'Summary, etc. at Google Book Search')
        output += '</a><br/>'
        output += '<a href="%s"><img src="http://www.google.com/intl/en/googlebooks/images/gbs_preview_button1.gif" /></a>' % top_result["volumeInfo"]["infoLink"]
        output += '</div>'
        return mark_safe(output)
    else:
        return '' 

def get_item_availablity(item_id):
    """
    Method conntects to ILS, retrieves item information, and generates
    corresponding html from template fragment.

    :param item_id: Item id
    :rtype: HTML
    """
    item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
    item_available_template = loader.get_template('item_availability.html')
    params = {'item':item_bot}
    context = Context(params)
    return mark_safe(item_available_template.render(context))

def get_item_status(item_id):
    """Method connects to ILS and retrieves the current circulation status
    of a an item.

    :param item_id: Item id, required
    :rtype: String of status
    """
    item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
    item_status = item_bot.status()
    if item_status is None:
        css_class = ''
    elif item_status.startswith('Due'):
        css_class = 'due-back'
    else:
        css_class = 'available'
    status_txt = '''<span class="%s">%s ''' % (css_class,item_status)
    volume = item_bot.volume()
    if volume is not None:
        status_txt += item_bot.volume()
    status_txt += '</span>'
    location = item_bot.location()
    if location is not None:
        if not location.startswith('Online'):
            status_txt += ' located in %s' % location
    call_number = item_bot.callnumber()
    if call_number is not None:
        status_txt += ' with call number <b>%s</b>' % call_number
    return mark_safe(status_txt) 

def get_marc_as_list(raw_marc):
    """Method takes Solr MARC format and splits into a list of field dictionarys

    :param raw_marc: Raw MARC string
    :rtype: List of field dictionary
    """
    output = []
    marc_listing = raw_marc.split("=")
    for row in marc_listing:
        output.append({'tag':row[0:3],
                      'value':row[3:]})
    return output
  

def get_refworks_url(record_id,hostname):
    """Generates a link for exporting citation to RefWorks.

    :param record_id: Bib ID of record
    :param hostname: Hostname of server
    :rtype: String
    """
    refworks_url = u'http://www.refworks.com/express/expressimport.asp?vendor=discover-aristotle&filter=RefWorks+Tagged+Format&url=http://%s/catalog/record/%s/refworks' % (hostname,record_id)
    return mark_safe(refworks_url)

def get_valid_url(raw_url):
    """
    Returns HTML snippet of URL by checking to see if it doesn't include
    View online or variations

    :param raw_url: URL string
    :rtype: String 
    """
    web_location = raw_url.lower().split("/")[-1]
    if not web_location.startswith('view'):
       html_str = '(<a href="%s">Online Location</a>)' % raw_url
       return mark_safe(html_str)
    else:
       return mark_safe('')

def generate_prospector_url(record_id):
    """Generates link to Prospector's union catalog

    :param record_id: Bib ID of record
    :rtype: String of URL to prospector
    """
    prospector_url = settings.PROSPECTOR_URL % (record_id,record_id)
    return mark_safe(prospector_url)

def reduce_subjects(doc):
    """Iterates and sort all topic and subject related fields and
    returns a set of unique subjects.

    :param doc: Dictionary of subject values from the Solr document
                query
    :rtype: Set of subject terms
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

def search_dropdown(search_type):
    """Sets drop-down button for the simple search to match the type,
    defaults to Keyword.
    
    :param search_type: Type of search (keyword, author, etc.) from
                        hidden input field
    :rtype: HTML String
    """
    if len(search_type) < 1:
        search_type = 'Keyword'
    return mark_safe('''<button type="submit" id="searchby" name="btnsubmit" class="btn" value="{0}">{0}</button>'''.format(search_type))

def search_field_options(search_type):
    """
    Generates a list of field search options

    :param search_type: Type of search, can be none 
    :rtype: HTML String 
    """
    output_html = ""
    field_types = [('keyword','Any Field'),
                   ('author','Author'),
                   ('title','Title'),
                   ('topic','Subject')]
    for row in field_types:
        output_html += '<option value="%s" ' % row[0]
        if search_type == row[0]:
            output_html += 'selected="SELECTED" '
        output_html += '>%s</option>' % row[1]
    return mark_safe(output_html)

def search_operator_options(bool_operator):
    """Generates a list of boolean search HTML options for
    AND, AND NOT, OR

    :param bool_operator: Boolean Operator, can be none
    :rtype: HTML String 
    """
    output_html = ''
    for row in ['AND','AND NOT','OR']:  
        output_html += '<option value="%s" ' % row
        if row == bool_operator:
             output_html += ' selected="SELECTED" '
        output_html += '>%s</option>' % row.title()
    return mark_safe(output_html)

register.filter('display_empty_facets',display_empty_facets)
register.filter('display_ill',display_ill)
register.filter('display_online',display_online)
register.filter('display_spellcheck',display_spellcheck)
register.filter('get_adjacent',get_adjacent)
register.filter('get_cover_image',get_cover_image)
register.filter('get_format_icon',get_format_icon)
register.filter('get_google_book',get_google_book) 
register.filter('get_item_availablity',get_item_availablity)
register.filter('get_item_status',get_item_status)
register.filter('get_marc_as_list',get_marc_as_list)
register.filter('get_refworks_url',get_refworks_url)
register.filter('get_valid_url',get_valid_url)
register.filter('generate_prospector_url',generate_prospector_url)
register.filter('reduce_subjects',reduce_subjects)
register.filter('search_dropdown',search_dropdown)
register.filter('search_field_options',search_field_options)
register.filter('search_operator_options',search_operator_options)

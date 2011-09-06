# Copyright 2007 Casey Durfee
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

from datetime import datetime
import pprint
import re
import string
import sys
import time
import urllib
import logging

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.utils import simplejson
from django.utils.encoding import iri_to_uri
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers

@vary_on_headers('accept-language', 'accept-encoding')
def index(request):
    cache_key = request.META['HTTP_HOST']
    response = cache.get(cache_key)
    if response:
        return response
    context = RequestContext(request)
    params = [
        ('rows', 0),
        ('facet', 'true'),
        ('facet.limit', settings.INDEX_FACET_TERMS),
        ('facet.mincount', 1),
        ('q.alt', '*:*'),
    ]
    for facet_option in settings.INDEX_FACETS:
        params.append(('facet.field', facet_option['field'] + '_facet'))
        # sort facets by name vs. count as per the config.py file        
        if not facet_option['sort_by_count']:
            params.append(('f.%s.facet.sort' % facet_option['field'], 
                'false'))
    solr_url, solr_response = get_solr_response(params)
    try:
        facet_fields = solr_response['facet_counts']['facet_fields']
    except KeyError, e:
        raise KeyError, 'Key not found in Solr response: %s' % e
    facets = []
    for facet_option in settings.INDEX_FACETS:
        field = facet_option['field']
        terms = facet_fields[field + '_facet']
        facet = {
            'terms': terms,
            'field': field,
            'name': facet_option['name'],
        }
        facets.append(facet)
    context['facets'] = facets
    context['INDEX_FACET_TERMS'] = settings.INDEX_FACET_TERMS
    template = loader.get_template('discovery/index.html')
    response = HttpResponse(template.render(context))
    if not settings.DEBUG:
        cache.set(cache_key, response)
    return response

@vary_on_headers('accept-language', 'accept-encoding')
def search(request):
    context = RequestContext(request)
    if request.GET.get('history'):
        template = loader.get_template('discovery/search_history.html')
        return HttpResponse(template.render(context))
    context.update(get_search_results(request))
    context['ILS'] = settings.ILS
    context['MAJAX_URL'] = settings.MAJAX_URL
    template = loader.get_template('discovery/index.html')
    return HttpResponse(template.render(context))

@vary_on_headers('accept-language', 'accept-encoding')
def record(request, record_id):
    context = RequestContext(request)
    solr_url, doc = get_record(record_id)
    context['doc'] = doc
    context['DEBUG'] = settings.DEBUG
    context['solr_url'] = solr_url
    base_params = [
        ('rows', 0),
        ('q.alt', '*:*'),
    ]
    subject_terms = []
    for subject in doc.get('subject', []):
        params = base_params[:]
        params.append(('fq', 'subject_facet:"%s"' % subject))
        solr_url, solr_response = get_solr_response(params)
        subject_terms.append((solr_response['response']['numFound'], subject))
    subject_terms.sort()
    subject_terms.reverse()
    subject_terms = [(x[1], x[0]) for x in subject_terms]
    context['subject_terms'] = subject_terms
    context['MAJAX_URL'] = settings.MAJAX_URL
    template = loader.get_template('discovery/record.html')
    return HttpResponse(template.render(context))

def unapi(request):
    context = RequestContext(request)
    identifier = request.GET.get('id')
    format = request.GET.get('format')
    if identifier and format:
        solr_url, doc = get_record(identifier)
        if format == 'oai_dc':
            # we'll include test for record_type when we have 
            # different types of records 
            #if doc['record_type'] == 'book':  
            element_map = {
                'identifier': ['isbn', 'upc'], 
                'title': ['title'], 
                'publisher': ['publisher'],
                'language': ['language'],
                'description': ['description'],
                'subject': ['subject'],
                'date': ['year'],
                'contributor': ['name'],
                'format': ['format'],
            }
            elements = []
            for name in element_map:
                elements.extend(get_elements(name, element_map[name], doc))
            context['elements'] = elements
            template = loader.get_template('discovery/unapi-oai_dc.xml')
            return HttpResponse(template.render(context), 
                    mimetype='application/xml')
        if format == 'mods':
            context['doc'] = doc
            template = loader.get_template('discovery/unapi-mods.xml')
            return HttpResponse(template.render(context), 
                    mimetype='application/xml')
        else:
            raise Http404 # should be 406 -- see http://unapi.info/specs/
    if identifier:
        context['id'] = identifier
    template = loader.get_template('discovery/unapi.xml')
    return HttpResponse(template.render(context), mimetype='application/xml')

def get_elements(name, fields, doc):
    elements = []
    for field in fields:
        if field in doc:
            field_values = doc[field]
            if not hasattr(field_values, '__iter__'):
                field_values = [field_values]
            for value in field_values:
                element = {'name': name, 'terms': []}
                if field == 'isbn':
                    element['terms'].append('ISBN:%s' % value)
                elif field == 'upc':
                    element['terms'].append('UPC:%s' % value)
                else:
                    element['terms'].append(value)
                elements.append(element)
    return elements

def get_record(id):
    id_query = 'id:%s' % id
    params = [
        ('q.alt', '*:*'),
        ('fq', id_query.encode('utf8')),
    ]
    solr_url, solr_response = get_solr_response(params)
    try:
        doc = solr_response['response']['docs'][0]
    except IndexError:
        raise Http404
    return (solr_url, doc)

LIMITS_RE = re.compile(r"""
(
  [+-]?      # grab an optional + or -
  [\w]+      # then a word 
):           # then a colon
(
  ".*?"|     # then anything surrounded by quotes 
  \(.*?\)|   # or parentheses
  \[.*?\]|   # or brackets,
  [\S]+      # or non-whitespace strings
)
""", re.VERBOSE | re.UNICODE)
def pull_limits(limits):
    """
    Pulls individual limit fields and queries out of a combined 
    "limits" string and returns (1) a list of limits and (2) a list
    of fq parameters, with "_facet" added to the end of each field, 
    to send on to Solr.
    """
    parsed_limits = LIMITS_RE.findall(limits)
    limit_list = []
    fq_params = []
    for limit in parsed_limits:
        field, query = limit
        limit = u'%s:%s' % (field, query)
        limit_list.append(limit)
        fq_param = u'%s_facet:%s' % (field, query)
        fq_params.append(fq_param)
    return limit_list, fq_params

POWER_SEARCH_RE = re.compile(r"""
".+?"|         # ignore anything surrounded by quotes
(
  (?:
    [+-]?      # grab an optional + or -
    [\w]+:     # then a word with a colon
  )
  (?:
    ".+?"|     # then anything surrounded by quotes 
    \(.+?\)|   # or parentheses
    \[.+?\]|   # or brackets,
    [\S]+      # or non-whitespace strings
  )
)
""", re.VERBOSE | re.UNICODE)
def pull_power(query):
    """
    Pulls "power search" parts out of the query.  It returns
    (1) the query without those parts and (2) a list of those parts.

    >>> query = 'title:"tar baby" "toni morrison" -topic:(dogs justice) fiction "the book:an adventure" +author:john'
    >>> pull_power(query)
    (' "toni morrison"  fiction "the book:an adventure" ', ['title:"tar baby"', '-topic:(dogs justice)', '+author:john'])
    >>> 
    """
    power_list = POWER_SEARCH_RE.findall(query)
    # drop empty strings
    power_list = [x for x in power_list if x] 
    # escape for re
    escaped_power = [re.escape(x) for x in power_list]
    powerless_query = re.sub('|'.join(escaped_power), '', query)
    return powerless_query, power_list

def get_solr_response(params):
    default_params = [
        ('wt', 'json'),
        ('fl','*'), # returns all of the fields
        ('json.nl', 'arrarr'), # for returning facets nicer
        ('qt', 'dismax'), # use DisMaxRequestHandler
    ]
    params.extend(default_params)
    urlparams = urllib.urlencode(params)
    url = '%sselect?%s' % (settings.SOLR_URL, urlparams)
    logging.error("SOLR URL is %s" % url)
    try:
        solr_response = urllib.urlopen(url)
    except IOError:
        raise IOError, 'Unable to connect to the Solr instance.'
    try:
        response = simplejson.load(solr_response)
    except ValueError, e:
        # Assign so error is in variables at Django error screen
        solr_error = urllib.urlopen(url).read()
        raise ValueError, 'Solr response was not a JSON object.'
    return url, response

def get_search_results(request): 
    query = request.GET.get('q', '')
    page_str = request.GET.get('page')
    try:
        page = int(page_str)
    except (TypeError, ValueError):
        page = 1
    #cache_key = '%s~%s' % (query, page)
    cache_key = request.META['QUERY_STRING']
    context = cache.get(cache_key)
    if context:
        return context
    context = {}
    context['current_sort'] = _('newest')
    context['sorts'] = [x[0] for x in settings.SORTS]
    zero_index = (settings.ITEMS_PER_PAGE * (page - 1))
    params = [
        ('rows', settings.ITEMS_PER_PAGE),
        ('facet', 'true'),
        ('facet.limit', settings.MAX_FACET_TERMS_EXPANDED),
        ('facet.mincount', 1),
        ('start', zero_index)
    ]
    for facet in settings.FACETS:
        params.append(('facet.field', facet['field'] + '_facet'))
        # sort facets by name vs. count as per the config.py file        
        if not facet['sort_by_count']:
            params.append(('f.%s.facet.sort' % facet['field'], 'false'))
    powerless_query, field_queries = pull_power(query)
    if not powerless_query.strip() or powerless_query == '*':
        params.append(('q.alt', '*:*'))
        context['sorts'] = [x[0] for x in settings.SORTS 
                if x[0] != _('relevance')]
    else:
        params.append(('q', powerless_query.encode('utf8')))
        context['current_sort'] = _('relevance')
    for field_query in field_queries:
        params.append(('fq', field_query.encode('utf8')))
    limits_param = request.GET.get('limits', '')
    limits, fq_params = pull_limits(limits_param)
    for fq_param in fq_params:
        params.append(('fq', fq_param.encode('utf8')))

    sort = request.GET.get('sort')
    if sort:
        context['current_sort'] = sort
        for sort_mapping in settings.SORTS:
            if sort_mapping[0] == sort:
                mapped_sort = sort_mapping[1]
        params.append(('sort', mapped_sort))
    # TODO: set up for nice display page for queries that return no results
    # or cause solr errors
    try:
        solr_url, solr_response = get_solr_response(params)
    except ValueError:
        return {'query': query}
    context.update(solr_response)

    # augment item results.
    count = 1
    for record in context['response']['docs']:
        record['count'] = count + zero_index
        count += 1
        record['name'] = record.get('personal_name', []) + \
                record.get('corporate_name', [])
        if settings.CATALOG_RECORD_URL:
            record['record_url'] = settings.CATALOG_RECORD_URL % record['id']
        else:
            record['record_url'] = reverse('discovery-record', 
                    args=[record['id']])
            
        #needed for amazon book covers and isbn to be displayable
        if 'isbn' in record:
            record['isbn_numeric'] = ''.join( [ x for x in record['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        #make an array out of Serials Solutions Name and URL
        if 'SSdata' in record:
            record['SSurldetails']=[]
            for items in record['SSdata']:
                SSurlitemdetails=items.split('|')
                record['SSurldetails'].append(SSurlitemdetails)
            
    # re-majigger facets 
    facet_counts = context['facet_counts']
    del context['facet_counts']
    facet_fields = facet_counts['facet_fields']
    facets = []   
    for facet_option in settings.FACETS:
        field = facet_option['field']
        all_terms = facet_fields[field + '_facet']
        terms = []
        # drop terms found in limits
        for term, count in all_terms:
            limit = '%s:"%s"' % (field, term)
            if limit not in limits:
                terms.append((term, count))
        if not terms:
            continue
        if len(terms) > settings.MAX_FACET_TERMS_BASIC:
            extended_terms = terms[settings.MAX_FACET_TERMS_BASIC:]
            terms = terms[:settings.MAX_FACET_TERMS_BASIC]
            has_more = True
        else:
            extended_terms = []
            has_more = False
        facet = {
            'terms': terms,
            'extended_terms': extended_terms,
            'field': field,
            'name': facet_option['name'],
            'has_more': has_more,
        }
        facets.append(facet)
        
    #find out if callnumlayerone is a limit and remove it from the facets 
    #dictionary if it is so that only callnumlayer2 is displayed (i.e. if 
    #100's dewey is limited, display the 10's)
    callnumlayeronefound = 0
    callnumlayertwofound = 0
    if limits:
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayerone':
                callnumlayeronefound = 1
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayertwo':
                callnumlayertwofound = 1
    #if callnumlayerone was not found to be a limit, remove 
    #callnumlayertwo so that only callnumlayerone displays 
    #(ie, show the 100's dewey only instead of 100's and 10's)
    if callnumlayeronefound == 1 or (callnumlayeronefound == 0 and callnumlayertwofound == 1): 
        count = 0
        for f in facets:
            if f['field'] == 'callnumlayerone':
                del facets[count]
                break
            count += 1
    
    if callnumlayeronefound == 0 or (callnumlayeronefound == 1 and callnumlayertwofound == 1): 
        count = 0
        for f in facets:
            if f['field'] == 'callnumlayertwo':
                del facets[count]
                break
            count += 1
            
    context['facets'] = facets
    context['format'] = request.GET.get('format', None)
    context['limits'] = limits
    context['limits_param'] = limits_param
    # limits_str for use in blocktrans 
    limits_str = _(' and ').join(['<strong>%s</strong>' % x for x in limits]) 
    context['limits_str'] = limits_str 
    full_query_str = get_full_query_str(query, limits)
    context['full_query_str'] = full_query_str
    context['get'] = request.META['QUERY_STRING']
    context['query'] = query
    number_found = context['response']['numFound']
    context['number_found'] = number_found
    context['start_number'] = zero_index + 1
    context['end_number'] = min(number_found, settings.ITEMS_PER_PAGE * page)
    context['pagination'] = do_pagination(page, number_found, 
            settings.ITEMS_PER_PAGE)
    context['DEBUG'] = settings.DEBUG
    context['solr_url'] = solr_url
    set_search_history(request, full_query_str)
    if not settings.DEBUG: 
        # only cache for production
        cache.set(cache_key, context, settings.SEARCH_CACHE_TIME)
    return context

def set_search_history(request, full_query_str):
    timestamp = datetime.now()
    search_data = (request.get_full_path(), full_query_str, timestamp)
    search_history = request.session.get('search_history')
    if search_history:
        # don't add it if it's the same as the last search
        #if search_history[0][0] != search_data[0]:
        #    search_history.insert(0, search_data)
        # remove earlier searches that are the same
        for past_search_data in search_history:
            if past_search_data[0] == search_data[0]:
                search_history.remove(past_search_data)
        search_history.insert(0, search_data)
    else:
        search_history = [search_data]
    request.session['search_history'] = search_history[:10]

def get_full_query_str(query, limits):
    # TODO: need to escape query and limits, then apply "safe" filter in 
    # template
    full_query_list = []
    if query:
        full_query_list.append('<strong>%s</strong>' % escape(query))
    else:
        full_query_list.append(_('everything'))
    if limits:
        full_query_list.append(_(' with '))
        limits_str = _(' and ').join(['<strong>%s</strong>' % escape(x) for x in limits]) 
        full_query_list.append(limits_str)
    return ''.join(full_query_list)

def do_pagination(this_page_num, total, per_page):
    if total % per_page:    
        last_page_num = (total // per_page) + 1
    else:
        last_page_num = (total // per_page)
    if this_page_num < 8:
        start_page_num = 1
    elif last_page_num - this_page_num < 7:
        start_page_num = max(last_page_num - 10, 1)
    else:
        start_page_num = this_page_num - 5
    end_page_num = min(last_page_num, start_page_num + 10)

    pages = []
    for page_num in range(start_page_num, end_page_num + 1):
        pages.append({
            'selected': page_num == this_page_num, 
            'start': ((page_num - 1) * per_page) + 1, 
            'end': min(total, page_num * per_page), 
            'number': page_num,
        })

    first_page = last_page = previous_page = next_page = None
    if start_page_num > 1:
        first_page = {
            'start': 1,
            'end': per_page,
            'number': 1,
        }
    if end_page_num < last_page_num:
        last_page = {
            'start': ((last_page_num - 1) * per_page) + 1,
            'end': total,
            'number': last_page_num,
        }
    if this_page_num > 1:
        previous_page_num = this_page_num - 1
        previous_page = {
            'start': ((previous_page_num - 1) * per_page) + 1,
            'end': previous_page_num * per_page,
            'number': previous_page_num,
        }
    if this_page_num < last_page_num:
        next_page_num = this_page_num + 1
        next_page = {
            'start': ((next_page_num - 1) * per_page) + 1,
            'end': next_page_num * per_page,
            'number': next_page_num,
        }

    variables = {
        'pages': pages, 
        'previous_page': previous_page,
        'next_page': next_page,
        'first_page': first_page,
        'last_page': last_page,
    }
    return variables

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
import logging,sunburnt
from templatetags.citation_extras import apa_name
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import *
from aristotle.help import help_loader

from django.conf import settings
from django.core import serializers
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sessions.models import Session
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.utils import simplejson
from django.utils.encoding import iri_to_uri
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers
from django.views.generic.simple import direct_to_template

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


@vary_on_headers('accept-language', 'accept-encoding')
def index(request):
    if request.META.has_key('HTTP_HOST'):
        cache_key = request.META['HTTP_HOST']
    else:
        cache_key = None
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
    context['help_loader'] = help_loader.help_loader
    template = loader.get_template('discovery/index.html')
    response = HttpResponse(template.render(context))
    if not settings.DEBUG:
        cache.set(cache_key, response)
    return response

@vary_on_headers('accept-language', 'accept-encoding')
def search(request):
    context = RequestContext(request)
    if request.GET.get('search-type'):
        search_type = request.GET['search-type']
        if search_type == 'author_search':
            context.update(get_specialized_results(request,'author'))
        elif search_type == 'title_search':
            context.update(get_specialized_results(request,'title'))
        elif search_type == 'subject_search':
            context.update(get_specialized_results(request,'subject'))
        elif search_type == 'journal_title_search':
            #! Should add extra format = 'journal'
            context.update(get_specialized_results(request,'subject'))
        if search_type != 'search':
            template = loader.get_template('discovery/index.html')
            return HttpResponse(template.render(context))
    if request.GET.get('history'):
        template = loader.get_template('discovery/search_history.html')
        return HttpResponse(template.render(context))
    context.update(get_search_results(request))
    context['ILS'] = settings.ILS
    context['MAJAX_URL'] = settings.MAJAX_URL
    context['help_loader'] = help_loader.help_loader
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
        params.append(('fq', 'subject_facet:"%s"' % subject.encode('ascii','ignore')))
        solr_url, solr_response = get_solr_response(params)
        subject_terms.append((solr_response['response']['numFound'], subject))
    subject_terms.sort()
    subject_terms.reverse()
    subject_terms = [(x[1], x[0]) for x in subject_terms]
    context['subject_terms'] = subject_terms
    context['MAJAX_URL'] = settings.MAJAX_URL
    context['session_id'] = request.session.session_key
    context['host_name'] = request.get_host()
    template = loader.get_template('discovery/record2.html')
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
    logging.error("SOLR URL=%s" % url)
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

def advanced_search(request):
    """
    Advanced search displays empty form for request.GET, displays
    results if request.POST

    :param request: Request from Client
    """
    solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
    facet_fields = ["%s_facet" % x['field'] for x in settings.FACETS]
    if request.method == 'GET':
        all_results = solr_server.search(q="*:*",
                                         **{'facet':'true',
                                            'facet.limit':settings.MAX_FACET_TERMS_EXPANDED,
                                            'facet.mincount':1,
                                            'facet.field':facet_fields})
        facets = []
        for facet_option in settings.FACETS:
            facet_name = '%s_facet' % facet_option['field']
            if all_results.facet_counts.facet_fields.has_key(facet_name):
                facet = {
                  'field': facet_option['field'],
                  'name': facet_option['name'],
                  'terms': all_results.facet_counts.facet_fields[facet_name],
                }
                facets.append(facet)
        number_found = all_results.numFound
        page_str = request.GET.get('page')
        try:
            page = int(page_str)
        except (TypeError, ValueError):
            page = 1
        zero_index = (settings.ITEMS_PER_PAGE * (page - 1))
        logging.error("In advanced_search page: {0} zero_index: {1} number_found: {2}".format(page,zero_index,number_found))
        return direct_to_template(request,
                                  'discovery/index.html',
                                  {'is_advanced_search':True,
                                   'end_number': min(number_found, settings.ITEMS_PER_PAGE * page),
                                   'facets':facets,
                                   'number_found': all_results.numFound,
                                   'pagination': do_pagination(page, 
                                                               number_found, 
                                                               settings.ITEMS_PER_PAGE),
                                   'start_number':zero_index + 1})
    else:
        # Use Sunburnt standard request handler
        field1_q = generate_Q(solr_server,
                              request.POST.get('field1_type',''),
                              request.POST.get('field1_phrase',''))
        field2_q = generate_Q(solr_server,
                              request.POST.get('field2_type',''),
                              request.POST.get('field2_phrase',''))
        operator_1 = request.POST.get('field1_operator','')
        solr_query = add_operator(field1_q,field2_q,operator_1)
        field3_q = generate_Q(solr_server,
                              request.POST.get('field3_type',''),
                              request.POST.get('field3_phrase',''))
        operator_2 = request.POST.get('field2_operator')
        solr_query = add_operator(solr_query,field3_q,operator_2)
        logging.error(facet_fields)
        adv_search_query = solr_server.query(solr_query).facet_by(facet_fields,
                                                                  limit=settings.MAX_FACET_TERMS_EXPANDED,
                                                                  mincount=1)
        solr_results = adv_search_query.execute()
        facets = []
        for facet_option in settings.FACETS:
            facet_name = '%s_facet' % facet_option['field']
            if solr_results.facet_counts.facet_fields.has_key(facet_name):
                facet = {
                  'field': facet_option['field'],
                  'name': facet_option['name'],
                  'terms': solr_results.facet_counts.facet_fields[facet_name],
                }
                facets.append(facet)
        for doc in solr_results.result.docs:
            if settings.CATALOG_RECORD_URL:
                doc['record_url'] = settings.CATALOG_RECORD_URL % doc['id']
            else:
                doc['record_url'] = reverse('discovery-record', 
                                            args=[doc['id']])
        context = {'docs':solr_results.result.docs}
        return direct_to_template(request,
                                  'discovery/index.html',
                                  {'advanced_query':request.POST,
                                   'is_advanced_search':True,
                                   'current_sort':_('newest'),
                                   'facets':facets,
                                   'limits_param':request.POST.get('limits', ''),
                                   'response':context,
                                   'sorts':[x[0] for x in settings.SORTS],
                                   'query':adv_search_query.query_obj.__unicode__()})



def generate_Q(solr_instance,field_type,value):
    """
    Helper function takes field type and value and parses out 
    values and returns a sunburnt.Q object or None

    :param solr_instance: Solr instance
    :param field_type: Search field type, should be keyword, author, title,
                       or subject
    :param value: Raw value from the field
    :rtype: sunburnt.Q instance or None
    """
    if value is None or len(value) < 1:
        return None
    if field_type == 'author':
        solr_query = solr_instance.Q()
        for raw_name in value.split(" "):
            name = raw_name.replace(".","")
            solr_query = solr_query & solr_instance.Q(author=name)
    elif field_type == 'topic':
        solr_query = solr_instance.Q(topic=value)
    elif field_type == 'title':
        solr_query = solr_instance.Q(title=value)
    else:
        solr_query = solr_instance.Q()
        for keyword in value.split(" "):
            solr_query = solr_query & solr_instance.Q(keyword)
    return solr_query

def add_operator(solr_Q1,solr_Q2,operator):
    """
    Function joins two Solr Qs with the correct operator

    :param solr_Q1: Solr Q object
    :param solr_Q2: Solr Q object
    :param operator: String, should be AND, OR, AND NOT
    """
    if solr_Q1 is not None and solr_Q2 is not None:
        if operator.strip() == 'AND NOT':
            return solr_Q1 & ~solr_Q2
        elif operator.strip() == 'OR':
            return solr_Q1 | solr_Q2
        # Defaults to AND
        else:
            return solr_Q1 & solr_Q2
    if solr_Q1 is not None and solr_Q2 is None:
        return solr_Q1
    if solr_Q1 is None and solr_Q2 is not None:
        return solr_Q2
    else:
        return None


def get_specialized_results(request,request_handler='dimax'):
    """
    Function queries Solr instance using :mod:`Sunburnt` for 
    specific types of request queries (author, title, subject)
    
    :param request: Request from client
    :param request_handler: Solr request type, default is dimax
    """
    solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
    query = request.GET.get('q')
    page_str = request.GET.get('page')
    try:
        page = int(page_str)
    except (TypeError, ValueError):
        page = 1
    cache_key = request.META['QUERY_STRING']
    context = cache.get(cache_key)
    if context is not None:
        return context
    context = {'docs':None}
    context['current_sort'] = _('newest')
    context['sorts'] = [x[0] for x in settings.SORTS]
    zero_index = (settings.ITEMS_PER_PAGE * (page - 1))
    limits_param = request.GET.get('limits', '')
    limits, fq_params = pull_limits(limits_param)
    if len(query) < 1:
        params = {'q':'*:*',
                  'facet':True,
                  'facet.limit':settings.MAX_FACET_TERMS_EXPANDED,
                  'facet.mincount':1,
                  'facet.field':[],
                  'start':zero_index,
                  'rows':settings.ITEMS_PER_PAGE}
    else:
        params = {'q':query,
                  'facet':True,
                  'facet.limit':settings.MAX_FACET_TERMS_EXPANDED,
                  'facet.mincount':1,
                  'facet.field':[],
                  'start':zero_index,
                  'rows':settings.ITEMS_PER_PAGE,
                  'fq':fq_params,
                  'qt':request_handler}
    for facet in settings.FACETS:
        params['facet.field'].append( facet['field'] + '_facet')
        # sort facets by name vs. count as per the config.py file        
        if not facet['sort_by_count']:
            params['f.%s.facet.sort' % facet['field']] = False
    solr_results = solr_server.search(**params)
    
    context['response'] = solr_results.result
    if solr_results.result.numFound > 0:
        count = 1   
        for doc in context['response'].docs:
            doc['count'] = count + zero_index
            count += 1
            doc['name'] = list(doc.get('personal_name',[])) + list(doc.get('corporate_name',[]))
            if settings.CATALOG_RECORD_URL:
                doc['record_url'] = settings.CATALOG_RECORD_URL % doc['id']
            else:
                doc['record_url'] = reverse('discovery-record', 
                                            args=[doc['id']])
            if 'isbn' in doc:
                doc['isbn_numeric'] = ''.join( [ x for x in doc['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
    else:
        if solr_results.spellcheck is not None:
            context['spellcheck'] = solr_results.spellcheck
    facet_counts = solr_results.facet_counts
    facet_fields = facet_counts.facet_fields
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
    number_found = context['response'].numFound
    context['number_found'] = number_found
    context['start_number'] = zero_index + 1
    context['end_number'] = min(number_found, settings.ITEMS_PER_PAGE * page)
    context['pagination'] = do_pagination(page, number_found, 
            settings.ITEMS_PER_PAGE)
    context['DEBUG'] = settings.DEBUG
    context['solr_url'] = settings.SOLR_URL 
    set_search_history(request, full_query_str)
    if not settings.DEBUG: 
        # only cache for production
        cache.set(cache_key, context, settings.SEARCH_CACHE_TIME)
    return context
            
def get_search_results(request):
    """
    Function returns search results from request

    :param request: Request object from client
    """ 
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

def add_item_cart(request):
    """Function accepts AJAX request for adding an item from either the 
    results or record display. The bib-number of the item is used as 
    an unique key of items.

    :param request: Client GET or POST Request 
    :rtype: Message string
    """
    if request.method == 'POST':
        # do something
        record_id = request.POST['record_id']
    else:
        # do something
        record_id = request.GET['record_id']
    items_cart = request.session.get('items_cart')
    if items_cart:
        if items_cart.count(record_id) < 1:
            items_cart.insert(0,record_id)
    else:
        items_cart = [record_id]
    request.session['items_cart'] = items_cart
    return HttpResponse('%s added to your list' % record_id)

def drop_item_cart(request):
    """Function accepts AJAX request for dropping an item from either the 
    results or record display. The bib-number of the item is used as 
    an unique key of items.

    :param request: Client GET or POST Request 
    :rtype: Message string
    """
    if request.method == 'POST':
        record_id = request.POST['record_id']
    else:
        record_id = request.GET['record_id']
    items_cart = request.session['items_cart']
    if items_cart:
        for item in items_cart:
            if item == record_id:
                items_cart.remove(item)
        request.session['items_cart'] = items_cart
        msg = '%s dropped from your list' % record_id
    else:
        msg = 'No items in your list'
    return HttpResponse(msg)

def email_cart(request):
    """Function emails contents of cart to provided email
    address.

    :param request: Client GET or POST Request 
    :rtype: Message string
    """
    if request.method == 'GET':
        to_email = request.GET['email']
    solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
    if not request.session.has_key('items_cart'):
        return HttpResponse('No email sent, you do not have any saved items')
    items_cart = request.session['items_cart']
    email_message = 'Your Saved Records\n'
    for i,item_id in enumerate(items_cart):
        solr_response = solr_server.search(q="id:%s" % item_id)
        if solr_response.result.numFound > 0:
            doc = solr_response.result.docs[0]
            email_message += '%s. %s' % (i+1,doc['full_title'])
            if doc.has_key('author'):
                email_message += ' by %s' % doc['author']
            email_message += '\n\t'
            if doc.has_key('callnum'):
                email_message += ' Call number: %s.' %  doc['callnum']
            if doc.has_key('location'):
                email_message += " Location: %s." % doc['location']
            if doc.has_key('format'):
                email_message += " Format: %s." %  doc['format']
            if doc.has_key('url'):
                for url in doc['url']:
                    email_message += '\n\tOnline at %s' % url
        email_message += "\n\n"
    send_mail('Exported records from Discovery Server', # Subject
              email_message, # Email body
              settings.EMAIL_HOST_USER,
              [to_email,],
              fail_silently=False)
    return HttpResponse('Email sent to %s from %s' % (to_email,settings.EMAIL_HOST_USER))

def get_cart(request):
    """Function returns all of the items in JSON format that 
    is the current session.

    :param request: Client GET or POST Request 
    :rtype: Message
    """
    records = []
    if request.session.get('items_cart',True):
        solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
        if request.session.has_key('items_cart'):
            items_cart = request.session['items_cart']
        else:
            items_cart = []
        for item_id in items_cart:
            solr_response = solr_server.search(q="id:%s" % item_id)
            if solr_response.result.numFound > 0:
                doc = solr_response.result.docs[0]
                rec_info = {'full_title':doc['full_title'],
                            'id':item_id}
                if doc.has_key('author'):
                    rec_info['author'] = doc['author']
                if doc.has_key('callnum'):
                    rec_info['callnum'] = doc['callnum']
                if doc.has_key('location'):
                    rec_info['location'] = doc['location']
                if doc.has_key('format'):
                    rec_info['format'] = doc['format']
                records.append(rec_info)
    data = simplejson.dumps(records)
    return HttpResponse(data,'application/javascript')
   

def print_cart(request):
    """Function returns HTML for printing of all items that are 
    in the current user's session.

    :param request: Request from client
    :rtype: HTML
    """
    records = []
    if request.session.has_key('items_cart'):
        solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
        items_cart = request.session['items_cart']
        for item_id in items_cart:
            solr_response = solr_server.search(q="id:%s" % item_id)
            if solr_response.result.numFound > 0:
                records.append(solr_response.result.docs[0])
    return direct_to_template(request,
                              'discovery/snippets/cart_print.html',
                              {'records':records})



def refworks_cart(request):
    """Function returns the contents in item carts as 
       RefWorks tagged format

    :param request: Client request
    :rtype: Text in RefWorks Tagged Format
    """
    response = HttpResponse(mimetype="text/plain")
    output = ''
    if request.GET.has_key("session"):
        session_id = request.GET['session']
        session = Session.objects.get(pk=session_id)
        session_vars = session.get_decoded()
    else:
        session_vars = request.session
    if session_vars.has_key('items_cart'):
        for item_id in session_vars['items_cart']:
            output += refworks_helper(item_id)
    response.write(output)
    return response

def refworks_item(request,record_id):
    """Function returns Refworks Tagged format for a single
    item id.

    :param request: Client request
    :param record_id: Record ID
    :rtype: Text in RefWorks Tagged Format
    """
    response = HttpResponse(mimetype="text/plain")
    output = refworks_helper(record_id)
    response.write(output)
    return response


def refworks_helper(item_id):
    """Helper function queries Solr for item and returns 
    a RefWork's tagged format for the item. 

    :param item_id: Item id
    :rtype: Text in RefWorks Tagged Format
    """
    output = ''
    solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
    solr_response = solr_server.search(q="id:%s" % item_id)
    if solr_response.result.numFound > 0:
        doc = solr_response.result.docs[0]
        if doc.has_key('format'):
            raw_format = doc['format'].lower()
            if raw_format.find('book') > -1:
                output += 'RT Book, Whole\n'
            elif raw_format.find('video'):
                output += 'RT Video/ DVD\n'
            elif raw_format.find('map') or raw_format.find('atlas'):
                output += 'RT Map\n'
            elif raw_format.find('electronic'):
                output += 'RT Web Page\n'
            elif raw_format.find('sound'):
                output += 'RT Sound Recording\n'
            else:
                output += 'RT Generic\n'
        output += 'SR Electronic(1)\n'
        output += 'ID %s\n' % doc['id']
        if doc.has_key('title'):
            output += 'T1 %s\n' % doc['title']
        if doc.has_key('author'):
            for author in doc['author']:
                output += 'A1 %s\n' % apa_name(author)
        if doc.has_key('pubyear'):
            output += 'YR %s\n' % doc['pubyear']
        if doc.has_key('publisher'):
            output += 'PB %s\n' % doc['publisher']
        output += "\n"
    return output

        

def cart_pdf(request):
    """Function generates a dynamic PDF for all of items that are
    in current session.

    :param request: Request from client
    :rtype: PDF for download 
    """
    response = HttpResponse(mimetype="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=saved_records.pdf'
    
    buffer = StringIO()
    
    #p = canvas.Canvas(buffer)
   
    styles =  getSampleStyleSheet()
    PAGE_HEIGHT = defaultPageSize[1]
    PAGE_WIDTH = defaultPageSize[0]
    title = 'Saved Records from Discovery Layer'
    doc = SimpleDocTemplate(buffer,
                            rightMargin=30,
                            leftMargin=20,
                            topMargin=30,
                            bottomMargin=15)
    Records = []
    default_style = styles["Normal"]
    if request.session.has_key('items_cart'):
        solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
        
        items_cart = request.session['items_cart']
        #p.setFont('Times-Bold',16)
        #p.drawString(inch,PAGE_HEIGHT-inch,"Your Saved Records from %s" % datetime.today().strftime("%B %d, %Y"))
        heading_txt = "Your Saved Records from %s" % datetime.today().strftime("%B %d, %Y")
        Records.append(Paragraph(heading_txt,styles["Heading1"]))
        Records.append(Spacer(1,0.2*inch))
        for i,item_id in enumerate(items_cart):
            solr_response = solr_server.search(q="id:%s" % item_id)
            if solr_response.result.numFound > 0:
                solr_doc = solr_response.result.docs[0]
                record_text = "%s. <b>%s</b> " % (i+1,solr_doc['full_title'])
                if solr_doc.has_key('callnum'):
                    record_text += "Call-number: %s" % solr_doc['callnum']
                if solr_doc.has_key('location'):
                    record_text += " at %s" % solr_doc['location'][0]
                if solr_doc.has_key('url'):
                    record_text += " %s" % solr_doc['url'][0]
                Records.append(Paragraph(record_text,default_style))
                Records.append(Spacer(1,0.2*inch))
                #p.saveState()
        doc.build(Records)
    else:
        pass
        #p.drawString(100,100,"You do not have any saved records")


    #p.showPage()
    #p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def get_all_items(request):
    """
    AJAX function takes a record id, and generates a table
    of all of the items associated with a record 
    including each item's circ status to display in a client-side 
    dialog.

    :param request: HTTP GET or POST request
    :rtype string: HTML string
    """
    record_id = request.REQUEST.get('record_id')
    solr_status,doc = get_record(record_id)
    return direct_to_template(request,
                              'discovery/snippets/all-items-dlg.html',
                              {'doc':doc})


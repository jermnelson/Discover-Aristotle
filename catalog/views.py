"""
 views.py - Aristotle Catalog Views Module
"""
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright: Currently copyrighted by Jeremy Nelson and Colorado College
#
import logging,urllib2,copy
from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
import catalog.settings,sunburnt,httplib2
from catalog.models import Comment


# Creates Solr Interface object
h = httplib2.Http(cache=catalog.settings.SOLR_CACHE)
solr_server = sunburnt.SolrInterface(catalog.settings.SOLR_URL,
                                     http_connection=h)

def author_search(request,author_phrase):
    """
    Author phrase search 
    """
    author_results = solr_server.search(q=author_phrase,
                                        facet=True,
                                        qt='author_search',
                                        wt='blacklight')
    facet_listing =  __facet_processing(author_results.facet_counts.facet_fields)
    return direct_to_template(request,
                              'catalog/index.html',
                              {'catalog_results':author_results,
                               'facet_listing':facet_listing})

def comment(request):
    """
    Stores comments for review
    """
    if request.method == 'POST':
        comment_text = request.POST['comment']
        if request.POST.has_key('creator'):
            creator = request.POST['creator']
        else:
            creator = 'anonymous'
        comment = Comment(created_by=creator,
                          text=comment_text)
        comment.save()
        request.session['message']  = '''<h2>Thank-you %s!</h2>
        Your comment below will be reviewed by Tutt Library Systems<br/><quote>%s</quote> 
        ''' % (creator,
               comment.text)
        return HttpResponseRedirect('/catalog/message')
    else:
        return HttpResponseRedirect('/')


def default(request):
    """
    Default view of Aristotle Catalog
    """
    catalog_results,facet_listing = None,[]
    if request.method == 'POST':
        search_phrase = request.POST['search_phrase']
        if len(search_phrase) > 0:
            qterms = [request.POST['search_phrase'],]
        else:
            qterms = []
        if request.POST.has_key('q'):
            qterms = qterms + request.POST.getlist('q')
        if request.POST.has_key('fq'):
            facet_q = request.POST.getlist('fq')
        else:
            facet_q = []
        if request.POST.has_key('search-type'):
            query_type = request.POST['search-type']
        else:
            query_type = 'search'
        if request.POST.has_key('start'):
            start = request.POST['start']
        else:
            start = 0
        if request.POST.has_key('rows'):
            rows = request.POST['rows']
        else:
            rows = 20
        catalog_results = solr_server.search(q=qterms,
                                             fl='*',
                                             fq=facet_q,
                                             facet=True,
                                             qt=query_type,
                                             rows=rows,
                                             start=start,
                                             wt='blacklight')
        facet_listing = __facet_processing(catalog_results.facet_counts.facet_fields)
    else:
        facet_result = __all_facets()
        if facet_result:
            facet_listing = facet_result
    return direct_to_template(request,
                              'catalog/index.html',
                              {'catalog_results':catalog_results,
                               'facet_listing':facet_listing})

def detail(request,solr_id):
    """
    Detail view of a single search result
    """
    catalog_results = solr_server.search(q="id:%s" % solr_id,
                                         fl='*',
                                         qt='document')
    return direct_to_template(request,
                              'catalog/detail.html',
                             {'record':catalog_results[0]})


def message(request):
    """
    Returns a message page to the user
    """
    message = request.session.get('message','No message')
    return direct_to_template(request,
                              'catalog/message.html',
                              {'message':mark_safe(message)})

def subject_search(request,subject_phrase):
    """
    Subject phrase search 
    """
    subject_results = solr_server.search(q=subject_phrase,
                                         facet=True,
                                         qt='subject_search',
                                         wt='blacklight')
    facet_listing =  __facet_processing(subject_results.facet_counts.facet_fields)
    return direct_to_template(request,
                              'catalog/index.html',
                              {'catalog_results':subject_results,
                               'facet_listing':facet_listing})


def title_search(request,title_phrase):
    """
    Title phrase search 
    """
    title_results = solr_server.search(q=title_phrase,
                                       facet=True,
                                       qt='title_search',
                                       wt='blacklight')
    facet_listing =  __facet_processing(title_results.facet_counts.facet_fields)
    return direct_to_template(request,
                              'catalog/index.html',
                              {'catalog_results':subject_results,
                               'facet_listing':facet_listing})



# View helper functions
def __all_facets():
    """
    Having issues with Python Solr libraries returning facets for the entire
    collection, using direct HTTP calls for now.
    """
    query_string = '''%s/select?q=*:*&qt=standard&facet=true&facet.limit=15&version=2.2&wt=python&rows=0''' % catalog.settings.SOLR_URL
    for field in catalog.settings.FACETS['default']:
        query_string += '&facet.field=%s' % field['facet_field']
    try:
        raw_result = urllib2.urlopen(query_string).read()
        
        solr_result = eval(raw_result)
    except:
        solr_result = None
    if solr_result is not None:
        solr_results = solr_result['facet_counts']['facet_fields']
        raw_facet_results = {}
        for k,v in solr_results.iteritems():
            tmp_results = copy.deepcopy(v)
            raw_facet_results[k] = []
            for row in tmp_results:
                tmp_tuple = (tmp_results.pop(0),tmp_results.pop(0))
                if type(tmp_tuple[0]) == int:
                    pass
                elif len(tmp_tuple[0]) < 2:
                    pass
                else:
                    raw_facet_results[k].append(tmp_tuple)
        return __facet_processing(raw_facet_results)
    else:
        return None
    

def __facets(search_terms):
    """
    Returns a list of facet results
    """   
    facet_listing,facet_fields = [],[] 
    for field in catalog.settings.FACETS['default']:
        facet_fields.append(field['facet_field'])
    facets_query = solr_server.query(search_terms[0])
    for term in search_terms[1:]:
        facets_query.query(term)
    facets_query.facet_by(facet_fields).paginate(rows=0)
    facet_results = facets_query.execute().facet_counts.facet_fields
    return __facet_processing(facet_results)


def alt__facet_processing(facet_results):
    output = []
    all_facets = {}
    for setting,fields in catalog.settings.FACETS.iteritems():
        for row in fields:
            all_facets[row['facet_field']] = row['label']
    for facet,value in facet_results.iteritems():
        facet_dict = {'field':facet,'facets':value}
        if all_facets.has_key(facet):
            facet_dict['label'] = all_facets[facet]
        else:
            facet_dict['label'] = facet.title()
        output.append(facet_dict)
    output.sort(key=lambda facet: facet['label'])
    return output
        

def __facet_processing(facet_results):
    """
    Cycles through solr result and returns a dict with the label
    and a list of facet results.
    """
    facet_listing = []
    for field in catalog.settings.FACETS['default']:
        if facet_results.has_key(field['facet_field']):
            facets = facet_results[field['facet_field']]
            if field.has_key('sort'):
                facets.sort()
            result = {'label':field['label'],
                      'field':field['facet_field'],
                      'facets':facets}
            facet_listing.append(result)
    return facet_listing

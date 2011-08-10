# 
# views.py - Aristotle Catalog Views Module
#
# Author: Jeremy Nelson
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
import catalog.settings 
from solr.bots.solrbots import SolrBot

# Creates Solr bot
solr_bot = SolrBot(solr_server=catalog.settings.SOLR_URL)

def default(request):
    """
    Default view of Aristotle Catalog
    """
    catalog_results,facet_listing = None,[]
    if request.method == 'POST':
        search_phrase = request.POST['search_phrase']
        search_query = solr_bot.solr_interface.query(search_phrase)
        catalog_results = search_query.execute()
        facet_listing = __facets(search_phrase)
    else:
        facet_result = __all_facets()
        if facet_result:
            facet_listing = facet_result
    return direct_to_template(request,
                              'catalog/index.html',
                              {'catalog_results':catalog_results,
                               'facet_listing':facet_listing})

def detail(request):
    """
    Detail view of a single search result
    """
    return direct_to_template(request,
                              'catalog/detail.html',
                             {})

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
    

def __facets(search_term=None):
    """
    Returns a list of facet results
    """   
    facet_listing,facet_fields = [],[] 
    for field in catalog.settings.FACETS['default']:
        facet_fields.append(field['facet_field'])
    facets_query = solr_bot.solr_interface.query(search_term).facet_by(facet_fields).paginate(rows=0)
    facet_results = facets_query.execute().facet_counts.facet_fields
    return __facet_processing(facet_results)

def __facet_processing(facet_results):
    """
    Cycles through solr result and returns a dict with the label
    and a list of facet results.
    """
    facet_listing = []
    for field in catalog.settings.FACETS['default']:
        facets = facet_results[field['facet_field']]
        facets.sort()
        result = {'label':field['label'],
                  'facets':facets}
        facet_listing.append(result)
    return facet_listing

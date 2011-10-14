"""
 views.py - Views for GoldRush Microservices Django Application 
"""
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
# Copyright: 2011 Colorado College

#
# 2011 (c) Colorado College
#
__author__ = 'Jeremy Nelson'

namespace = 'grx'

from django.views.generic.simple import direct_to_template
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse,Http404,HttpResponseRedirect
from grx.bots.grxbots import GoldRushBot
from grx.bots.solrbots import SolrBot
import grx.settings
from grx.models import *


# Sets up bots from in grx settings values
grx_bot = GoldRushBot(institutional_code=grx.settings.INSTITUTIONAL_CODE)
solr_bot = SolrBot(solr_server=grx.settings.SOLR_URL)
a_to_m = ['a','b','c','d','e','f','g','h','i','j','k','l','m']
n_to_z =['n','o','p','q','r','s','t','u','v','w','x','y','z']
search_browse_types=[{"label":"Search Keyword",
                      "grx_action":"searchByKeyword",
                      "hint":"Search for terms appearing anywhere in the journal title, including alternate titles."},
                     {"label":"Search Journal Title",
                      "grx_action":"searchByJrnlTitle",
                      "hint":"Search for a journal title as a phrase."},
                     {"label":"Search Subject",
                      "grx_action":"searchBySubject",
                      "hint":"Search for journals under a particular subject."},
                     {"label":"Search ISSN",
                      "grx_action":"searchByISSN",
                      "hint":"Search journal by ISSN, a unique identifying number consisting of 8 digits. Search with or without hyphen."},
                     {"label":"Browse Full Text Journal Title",
                      "grx_action":"browseJrnlFT",
                      "hint":"Browse journal titles that have full text."},
                     {"label":"Browse Journal Title",
                      "grx_action":"browseJrnl",
                      "hint":"Browse journal titles that have full text and/or indexing."},
                     {"label":"Browse Subject", 
                      "grx_action":"browseJrnlSubjects",
                      "hint":"Browse journals by subject."},
                     ]



def default(request):
    subjects = Subject.objects.all().order_by('name')
    subjects_dbs = []
    return direct_to_template(request,
                              'grx/index.html',
                              {'titles':[],
                               'a_to_m':a_to_m,
                               'n_to_z':n_to_z,
                               'subjects':subjects,
                               'search_types':search_browse_types})


# JSON Handler
def rpc(request):
    """JSON request handler, matches and calls methods from grx rpc module"""
    func_name = request.POST.get('func')
    #json_results = grx.rpc.rpc_handler(request)
    json_results = []
    return HttpResponse(json.dumps(json_results), 
                        mimetype='application/javascript')


def search(request):
    """Searches Goldrush Solr core"""
    query,grx_action = None,None
    if request.method == 'POST':
        query = request.POST['q']
        grx_action = request.POST['search-type']
    elif request.method == 'GET':
        query = request.GET['q']
        grx_action = request.GET['search-type']
    grx_search_results = {'query':query,
                          'journals':grx_bot.search(query,
                                                    action=grx_action,
                                                    limit=None)}
    return direct_to_template(request,
                                  'grx/index.html',
                                  {'title':'Searching GoldRush for %s' % query,
                                   'a_to_m':a_to_m,
                                   'n_to_z':n_to_z,
                                   'grx_results':None,
                                   'limits':[{'query':query},],
                                   'search_types':search_browse_types,
                                   'grx_search_results':grx_search_results,
                                   'subjects':None})

def subjects(request,subject=None):
    """Displays legacy HTML of subjects."""
    subjects = Subject.objects.all()
    if subject is None:
        return direct_to_template(request,
                                  'grx/subjects.html',
                                  {'subjects':subjects})
    else:
        grx_results = []
        raw_results = grx_bot.getDatabasesBySubject(subject)
        for row in raw_results:
            solr_result = solr_bot.searchForTitle(row['title'])
            if solr_result:
                grx_results.append(solr_result)
            else:
                grx_results.append(row)    
        return direct_to_template(request,
                                  'grx/index.html',
                                  {'title':'%s Databases' % subject,
                                   'a_to_m':a_to_m,
                                   'n_to_z':n_to_z,
                                   'grx_results':grx_results,
                                   'subjects':subjects})

def titles(request,alpha=None):
    """Displays legacy HTML of all databases that start with alpha, 
     otherwise display an A-Z list of entire collection from 
     Gold Rush.
    """
    if alpha is None:
        return direct_to_template(request,
                                  'grx/titles.html',
                                  {'titles':None})
    else:
        grx_results = []
        raw_results = grx_bot.getDatabasesByAlpha(alpha)
        for row in raw_results:
            solr_result = solr_bot.searchForTitle(row[1])
            if solr_result:
                grx_results.append(solr_result)
            else:
                grx_results.append(grx_bot.getDatabaseDetail(grxid=row[0]))    
        return direct_to_template(request,
                                  'grx/index.html',
                                  {'title':'%s Databases' % alpha.upper(),
                                  'a_to_m':a_to_m,
                                  'n_to_z':n_to_z,
                                  'grx_results':grx_results,
                                  'subjects':Subject.objects.all()})
        
        

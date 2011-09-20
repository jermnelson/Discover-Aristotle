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

def default(request):
    subjects = Subject.objects.all()
    subjects_dbs = []
    return direct_to_template(request,
                              'grx/index.html',
                              {'titles':[],
                               'a_to_m':a_to_m,
                               'n_to_z':n_to_z,
                               'subjects':subjects})


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
    if request.method == 'POST':
        query = request.POST['search_phrase']
        pass
    return HttpResponse('IN SEARCH query is %s' % request.POST['search_phrase'])

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
        
        

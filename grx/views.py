#
# view.py
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
import grx.settings
from grx.models import *
#import grx.rpc
from solr.bots.solrbots import SolrBot


# Sets up bots from in grx settings values
grx_bot = GoldRushBot(institutional_code=grx.settings.INSTITUTIONAL_CODE)
solr_bot = SolrBot(solr_server=grx.settings.SOLR_URL)


def default(request):
    subjects = Subject.objects.all()
    subjects_dbs = []
    for row in subjects:
        rec = {'name':row.name,
               'databases':grx_bot.getDatabasesBySubject(row.name)}
        subjects_dbs.append(rec)
    return direct_to_template(request,
                              'grx/index.html',
                              {'titles':[],
                               'subjects':subjects_dbs})

def top_facets(request):
    subjects = Subject.objects.all().order_by('name')
    letters = ['A','B','C','D','E','F','G','H','I','J','K',
               'L','M','N','O','P','R','S','T','V','W']
    letter_children = []
    for letter in letters:
        letter_children.append({'data': {'title':letter,
                                         'attr':{'href':"javascript:LoadTitles('%s')" % letter}}})
    subject_children = []
    for subject in subjects:
         subject_children.append({'data': {'title':subject.name,
                                           'attr':{'href':"javascript:LoadSubject('%s')" % subject.name}}})
               
    facet_results = [{'data':'Titles',
                      'children':letter_children},
                     {'data':'Subjects',
                      'children':subject_children}]
    return HttpResponse(json.dumps(facet_results), 
                        mimetype='application/javascript')

    

def legacy(request):
    """Displays legacy HTML from old Tutt Library website"""
    return direct_to_template()

# JSON Handler
def rpc(request):
    """JSON request handler, matches and calls methods from grx rpc module"""
    func_name = request.POST.get('func')
    #json_results = grx.rpc.rpc_handler(request)
    json_results = []
    return HttpResponse(json.dumps(json_results), 
                        mimetype='application/javascript')


def subjects(request,subject=None):
    """Displays legacy HTML of subjects."""
    subjects = Subject.objects.all()
    if subject is None:
        return direct_to_template(request,
                                  'grx/subjects.html',
                                  {'subjects':subjects})
    else:
        return direct_to_template(request,
                                  'grx/databases-by-subject.html',
                                  {'title':'%s Databases' % subject,
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
        return direct_to_template(request,
                                  'grx/databases-by-title.html',
                                  {'title':'%s Databases' % alpha.upper()})
        
        

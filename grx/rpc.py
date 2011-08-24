#
# rpc.py
#
# (c) 2011 Colorado College
#
__author__ = 'Jeremy Nelson'

namespace = 'grx'

import django.utils.simplejson as json
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseForbidden,HttpResponseRedirect
import logging,grx.settings
from grx.bots.grxbots import GoldRushBot
from solr.bots.solrbots import SolrBot
from grx.models import *

grx_bot = GoldRushBot(institutional_code=grx.settings.INSTITUTIONAL_CODE)
solr_bot = SolrBot(solr_server=grx.settings.SOLR_URL)


class JSONMicroservices(object):

    def __init__(self):
        # Loads all existing database filters into class 
        # variable instead of doing a db look-up each time.
        self.title_stems = DatabaseNameStemmer.objects.all()

    def __stemTitle(self,raw_title):
        """Searches for any raw_titles that start with the list
           of stemmed titles, returns stemmed title if found or
           the original raw_title if not"""
        for stem in self.title_stems:
            if raw_title.startswith(stem.starts_with):
                return stem.database_name
        return raw_title

    def loadFacet(self,request):
        facet_type = request.GET.get('type')
        value = request.GET.get('value')
        db_dict = dict()
        if facet_type == 'subject':
            databases = grx_bot.getDatabaseBySubject(value)
        elif facet_type == 'title':
            databases = grx_bot.getDatabasesByAlpha(value)
        for row in databases:
            grx_title = self.__stemTitle(row[1])
            solr_result = solr_bot.searchForTitle(title=grx_title)
            if solr_result is None:
                result = grx_bot.getDatabaseDetail(grxid=row[0])
            else:
                result = solr_result
            if not db_dict.has_key(grx_title):
                db_dict[grx_title] = result
        entries = db_dict.items()
        entries.sort(key=lambda x: x[1]['title'])
        return entries


def rpc_handler(request):
    # Assumes all GET requests are public
    func_name = request.GET['func']
    if func_name.startswith('_'):
        return HttpResponseForbidden()
    json_rpc = JSONMicroservices()
    if hasattr(json_rpc,'%s' % func_name):
        json_result = getattr(json_rpc,'%s' % func_name)(request)
        return HttpResponse(json.dumps(json_result),
                            mimetype='application/javascript')
    else:
        return HttpResponseNotFound()
   


def get_database_set(request):
    db_dict = {}
    if request.POST.has_key('filter'):
        db_filter = request.POST.get('filter')
    else:
        db_filter = None
    if request.POST.has_key('value'):
        value = request.POST.get('value')
    if db_filter == 'alpha':
        databases = grx_bot.getDatabasesByAlpha(value)
    elif db_filter == 'subject':
        databases = grx_bot.getDatabaseBySubject(value)
    for row in databases:
        grx_title = stem_title(row[1])
        solr_result = solr_bot.searchForTitle(title=grx_title)
        if solr_result is None:
            result = grx_bot.getDatabaseDetail(grxid=row[0])
        if not db_dict.has_key(grx_title):
            db_dict[grx_title] = result
    entries = db_dict.items()
    entries.sort(key=lambda x: x[1]['title'])
    json_result = {'data':db_filter,
                   'state':'closed',
                   'children':entries}
    return HttpResponse(json.dumps(json_result),
                        mimetype='application/javascript')
    

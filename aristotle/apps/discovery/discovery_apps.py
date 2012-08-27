#
# `discovery_apps`:module is a lightweight JSON wrapper that creates class
# stubs for the `Aristotle Library Apps </apps>`_.
#
#
__author__ = "Jeremy Nelson"
from django.conf import settings
from mysolr import Solr
import json,urllib,urllib2,os


class call_number_app(object):

    def __init__(self,**kwargs):
        """
        The `call_number_app` takes a number of optional parameters
        including an URL where the Aristotle Library Apps instance
        is currently running.

        :param url: URL of Aristotle Library Apps path to the call 
                    number app, defaults to 
                    http://0.0.0.0/apps/call_number/json/.
        """
        if kwargs.has_key("url"):
            self.call_number_url = kwargs.get("url")
        else:
            self.call_number_url = "http://0.0.0.0/apps/call_number/json/"
        self.solr = Solr(base_url=settings.SOLR_URL)

    def json_search(self,request):
        """
        Performs a call number search using JSON interface to the call 
        number app. Results are returned as JSON.

        :param request: Django request
        """
        call_number = request.REQUEST.get('q')
        if request.REQUEST.has_key("number_type"):
            number_type = request.REQUEST.get('number_type')
        else:
            number_type = 'lccn'
        context = {'docs':None}
        json_search_url = os.path.join(self.call_number_url,
                                       'term_search')
        json_search_url = "{0}?call_number={1}&slice-size={2}&type={3}".format(json_search_url,
                                                                               call_number.strip(),
                                                                               int(settings.ITEMS_PER_PAGE) - 3,
                                                                               number_type)
                                  
        json_results = urllib2.urlopen(json_search_url).read()
        results = json.load(urllib2.urlopen(json_search_url))
        if len(results.get("bib_numbers")) > 0:
            context['docs'] = []
            for bib_num in results.get("bib_numbers"):
                query = {"q":bib_num,
                         "qt":"dismax",
                         "fl":"*"}
                response = self.solr.search(**query)
                for doc in response.documents:
                    context["docs"].append(doc)
            # Iterate through and create record_urls
            for doc in context['docs']:
                doc['record_url'] = settings.CATALOG_RECORD_URL.format(doc['id'])
        context['current_sort'] = None
        context['sorts'] = [x[0] for x in settings.SORTS]
        context['start_number'] = 1
        context['end_number'] = min(results,
                                    settings.ITEMS_PER_PAGE)
        return context

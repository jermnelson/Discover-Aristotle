#
# solrbots.py
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
import re,sunburnt,httplib2
import datetime,sys,urllib

from operator import itemgetter
coverage_re = re.compile(r'(Coverage:\s*\w*\s*\w*\s*.*)')

class SolrBot(object):
    """
    `SolrBot` is the base bot for connecting to Solr server and retrieving
    and evaluating the results to a native Python object.
    """

    def __init__(self,**kwargs):
        """
        `SolrBot` initializes an instance of a bot

        Parameters:
        `solr_server`: URL to Solr server, defaults to 
                        http://0.0.0.0:8983/solr
        `query`: Solr query, optional
        `cache`: Solr cache location, optional
        """
        if kwargs.has_key('solr_server'):
            self.solr_server = kwargs.get('solr_server')
        else:
            self.solr_server = 'http://0.0.0.0:8983/solr'
        if kwargs.has_key('query'):
            self.query = kwargs.get('query')
        else:
            self.query = None
        if kwargs.has_key('cache'):
            self.cache_location = kwargs.get('cache')
        else:
            self.cache_location = 'solr/solr_cache'
        h = httplib2.Http(cache=self.cache_location)
        try:
            self.solr_interface = sunburnt.SolrInterface(url=self.solr_server,
                                                         http_connection=h)
        except:
            self.solr_interface = None
        

    def search(self):
        """
        Method attempts to submit a search query to the Solr
        server, evaluates and saves the result.
        """
        try:
            pass
        except:
            print("ERROR %s trying to get %s" % (sys.exc_info()[0],
                                                 self.query))
            self.result = None


    def searchForTitle(self,title,**kwargs):
        """
        Method takes a title and search Solr for 
        record. Returns a dict of the top result.

        Parameters:
        - `title`: Raw title, required
        """
        title = urllib.quote_plus(title)
        title_result = self.solr_interface.search(q='%s' % title,
                                                  fl='title_display,notes_grx_display,title_grx,url_fulltext_display,url_suppl_display',
                                                  qt='goldrush',
                                                  wt='blacklight',
                                                  version='2.2')
        if title_result.result.numFound > 0:
            top_result = title_result.result.docs[0]
            if top_result.has_key('url_fulltext_display'):
                url = top_result['url_fulltext_display'][0]
            elif top_result.has_key('url_suppl_display'):
                url = top_result['url_suppl_display']
            else:
                url = 'No URL provided'
            if top_result.has_key('notes_grx_display'):
                raw_note = top_result['notes_grx_display'][0]
            else:
                raw_note = 'No full text display'
            if coverage_re.search(raw_note):
                coverage = coverage_re.search(raw_note).groups()[0]
                clean_note = coverage_re.sub('',raw_note)
            else:
                coverage = 'Coverage: N/A'
                clean_note = raw_note
            return {'title':top_result['title_display'],
                    'url':url,
                    'updated':datetime.datetime.today().isoformat(),
                    'coverage':coverage,
                    'note':clean_note}
        else:
            return None

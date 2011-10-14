#
# grxbots.py
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
__author__ = 'Jeremy Nelson'
import datetime
from suds.client import Client

class GoldRushBot(object):
    """`GoldRushBot` uses the Colorado Alliance of Research Libraries Open URL and
    bibliographic database management XML web services to retrieve information
    specific to a single institution.
    """

    def __init__(self,**kwargs):
        if kwargs.has_key('grx_wsdl'):
            grx_wsdl = kwargs.get('grx_wsdl')
        else:
            grx_wsdl = 'http://grx.coalliance.org/grx.php?wsdl'
        if kwargs.has_key('institutional_code'):
            self.inst_code = kwargs.get('institutional_code')
        else:
            self.inst_code = '001_CCL'
        self.web_client = Client(grx_wsdl)
        # Searches for databases with a subject descriptor of 
        # 'Journals` to filter out from return values in method
        # calls ! FILTER LIST SHOULD BE PASSED IN FROM CREATING PROGRAM
        self.excluded_databases = []
        grx_results = self.web_client.service.browseDBCategory(self.inst_code,
                                                               'Journals')
        if hasattr(grx_results,'brief_recs'):
            brief_recs = grx_results.brief_recs
            if len(brief_recs) < 1:
                return output
            for row in brief_recs[0].itemlist:
                self.excluded_databases.append(row[0])

    def getAllDatabases(self):
        """
        Method returns a listing of database id and titles excluding
        databases that are flagged as journals.
        """
        raw_results = self.web_client.service.databaseListA2Z(self.inst_code)
        output = []
        for row in raw_results.brief_recs:
            if self.excluded_databases.count(row.dbid) < 1:
                output.append((row.dbid,row.dbtitle))
        return output

    def getDatabasesByAlpha(self,char):
        """
        Method takes a character and returns all of the databases with 
        a title that starts with the character.

        Parameters:
        - `char`: Character to search on, required
        """
        raw_results = self.web_client.service.browseDB(self.inst_code,char)
        output = []
        for row in raw_results.brief_recs:
            if self.excluded_databases.count(row.dbid) < 1:
                output.append((row.dbid,row.dbtitle))
        return output


    def getDatabaseDetail(self,
                          grxid=None,
                          title=None):
        """
        Method takes either a gold rush db id or a title. If db id is 
        provided, directly calls Gold Rush XML method. If title, 
        searches Gold Rush for title and returns a dictionary of the
        result.

        Parameters:
        - `grxid` - Gold Rush database id, optional
        - `title` - Title of database, optional
        """
        # Title and grxid cannot both be None
        if grxid is None and title is None:
            raise ValueError('grx_bot.getDatabaseDetail requires either a '\
                             'gold rush database id or a title')
        output = dict()
        if grxid is not None:
            try:
                raw_result = self.web_client.service.fullDBRec(self.inst_code,
                                                               grxid)
                full_rec = raw_result.full_rec
            except:
                print("ERROR retriving %s" % grxid)
                full_rec = None 
        elif title is not None:
            raw_result = self.web_client.service.searchByDBTitle(self.inst_code,
                                                                 title,
                                                                 False,
                                                                 False)
            # Title matched more than one Gold Rush database
            if len(raw_result.brief_recs) > 1:
                full_rec = None
            if len(raw_result.found_resource) > 0:
                full_rec = raw_result.found_resource.full_rec
        if full_rec is not None:
            output['title'] = full_rec.dbname
            output['updated'] = datetime.datetime.today().isoformat()
            output['note'] = full_rec.dbdescription
            output['coverage'] = 'Coverage: N/A'
            output['url'] = full_rec.provlist[0].dburl
            return output
 

    def getDatabasesBySubject(self,subject):
        """
        Method takes a subject term and returns all of the databases
        that GoldRush matches to this term.
        
        Paramters:
        - `subject`: Subject term to search on, required
        """
        raw_results = self.web_client.service.browseDBCategory(self.inst_code,
                                                               subject)
        output = []
        if hasattr(raw_results,'brief_recs'):
            brief_recs = raw_results.brief_recs
            if len(brief_recs) < 1:
                return output
            for row in brief_recs:
                for item in row.itemlist:
                    if self.excluded_databases.count(item[0]) < 1:
                        result = self.getDatabaseDetail(grxid=item[0])
                        if result is not None:
                            output.append(result)
        return output

    def search(self,query_term,action,limit=20):
        """
        Method takes user search term and queries Gold Rush's
        web-service 'action' method to display the journals matching 
        user's search query.
        """
        if not hasattr(self.web_client.service,action):
            raise ValueError("%s not found in Gold Rush" % action)
        
        grx_method = getattr(self.web_client.service,action)
        brief_hits = grx_method(self.inst_code,query_term)
        records = []
        # Iterate through the hits up to the limit
        for brief_rec in brief_hits.brief_recs[:limit]:
            result = self.web_client.service.fullJTRec(self.inst_code,
                                                       brief_rec.id)
            if not result.grx_error:
                records.append(result.full_rec)
        return records


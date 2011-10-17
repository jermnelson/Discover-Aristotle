#
# iiibots.py -- Bots for interfacing with III's Millennium system
#
# author: Jeremy Nelson
#
# Copyrighted by Colorado College
import urllib2,logging,datetime
import csv
from eulxml import xmlmap
from vendors.iii.models import ItemRecord,IIIStatusCode,Fund,FundProcessLog
from discovery.parsers.tutt_maps import LOCATION_CODE_MAP

class FundBot(object):
    """
    `FundBot` takes a csv file, search and replaces each occurrence of a FUND
    code with its full account value.
    """

    def __init__(self,**kwargs):
        """
        Initalizes bot with csv file reader
   
        :param  fund-csv-file: CSV file object 
        :param code-location: Field location index 0 where fund codes are located in 
                              the row, default is 4
        """
        if not kwargs.has_key('input-csv-file'):
            raise ValueError("FundBot requires a input-csv-file")
        self.input_csv = csv.Reader(kwargs.get('input-csv-file'))
        if kwargs.has_key('code-location'):
            self.code_location = int(kwargs.get('code-location'))
        else:
            self.code_location = 4
        

    
    def process(self):
        """
        Iterates through csv file, replacing each occurrence of fund code 
        with the expanded fund account value.
     
        :rtype: file object
        """
        subsitutions = 0
        self.output_csv = csv.Writer()
        for row in self.input_csv:
            fund_codes = row[self.code_location]
            for code in fund_codes:
                 fund = Fund(code=code)
                 
        


class ItemBot(object):
    """`ItemBot` uses the eulxml module to capture specific information about an
    item in a III Millennium ILS from a method call to a web OPAC in XML mode.
    """

    def __init__(self,**kwargs):
        """
        Initializes web OPAC address from passed in variable.
        """
        if kwargs.has_key('opac_url'):
            self.opac_url  = kwargs.get('opac_url')
        else:
            self.opac_url = None
        if kwargs.has_key('item_id'):
            self.item_id = kwargs.get('item_id')
            raw_xml_url = self.opac_url + self.item_id
            try:
                raw_xml = urllib2.urlopen(raw_xml_url).read()
                self.item_xml = xmlmap.load_xmlobject_from_string(raw_xml,xmlclass=ItemRecord) 
            except:
                logging.error("ERROR with %s" % raw_xml_url)
                self.item_xml = None 
        else:
            self.item_id = None

    def location(self):
        """
        Retrieves location code from XML and then does a look-up
        using the discovery.parsers.tutt_map LOCATION_CODE_MAP
        for the human-friendly facet label

        :rtype: string
        """
        location = None
        if self.item_xml is not None:
            try:
                location = LOCATION_CODE_MAP[self.item_xml.location_code.strip()]
            except KeyError:
                location = 'Unknown location code %s' % self.item_xml.location_code
        return location

    def status(self):
        """
        Retrieves status code from XML

        :rtype: string or None
        """
        if self.item_xml is not None:
            try:
                status = IIIStatusCode.objects.get(code=self.item_xml.status)
            except:
                status = None
            try:
                due_date = datetime.datetime.strptime(self.item_xml.due_date,'%m-%d-%Y')
                return 'Due back on %s' % due_date.strftime('%m-%d-%Y')
            except ValueError:
                pass # Failed to parse due-date, assume item is not checked-out
        else:
            return None
        if status is None:
            return 'Status unknown for code %s' % self.item_xml.status
        else:
            return status.value

    def volume(self):
        """
        Method retrieves Volume from XML or None if not present.

        :rtype: string
        """
        if self.item_xml is not None:
            if self.item_xml.volume is not None:
                return 'v. %s' % self.item_xml.volume
        return None
            
 

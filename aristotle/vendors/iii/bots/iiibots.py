#
# iiibots.py -- Bots for interfacing with III's Millennium system
#
# author: Jeremy Nelson
#
# Copyrighted by Colorado College
import urllib2,logging,datetime
from eulxml import xmlmap
from vendors.iii.models import ItemRecord,IIIStatusCode
from discovery.parsers.tutt_maps import LOCATION_CODE_MAP

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
        """
        if self.item_xml is not None:
            if self.item_xml.volume is not None:
                return 'v. %s' % self.item_xml.volume
        return None
            
 

#
# iiibots.py -- Bots for interfacing with III's Millennium system
#
# author: Jeremy Nelson
#
# Copyrighted by Colorado College
import urllib2,logging,datetime
from eulxml import xmlmap
from vendors.iii.models import ItemRecord,IIIStatusCode

class ItemBot(object):

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
                self.item_xml = None 
        else:
            self.item_id = None

    def status(self):
        """
        Method retrieves status code from XML
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
 

#
# iiibots.py -- Bots for interfacing with III's Millennium system
#
# author: Jeremy Nelson
#
# Copyrighted by Colorado College
import urllib2
from eulxml import xmlmap
from vendors.iii.models import ItemRecord

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
            raw_xml = urllib2.urlopen(raw_xml_url).read()
            self.item_xml = xmlmap.load_xmlobject_from_string(raw_xml,xmlclass=ItemRecord)  
        else:
            self.item_id = None

    def status(self):
        """
        Method retrieves status code from XML
        """
        return self.item_xml.status
 

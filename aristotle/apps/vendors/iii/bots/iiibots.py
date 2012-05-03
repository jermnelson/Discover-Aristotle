
# iiibots.py -- Bots for interfacing with III's Millennium system
#
# author: Jeremy Nelson
#
# Copyrighted by Colorado College
import urllib2,logging,datetime
import csv,re
from eulxml import xmlmap
from vendors.iii.models import ItemRecord,IIIStatusCode,Fund,FundProcessLog
from discovery.parsers.tutt_maps import LOCATION_CODE_MAP
from settings import ILS_PATRON_URL
from BeautifulSoup import BeautifulSoup

class FundBot(object):
    """
    `FundBot` takes a csv file, search and replaces each occurrence of a FUND
    code with its full account value.
    """

    def __init__(self,**kwargs):
        """
        Initalizes bot with csv file reader
   
        :param  csv_file: CSV file object 
        :param code_location: Field location index 0 where fund codes are located in 
                              the row, default is 9
        :param program_code: Suffix program code required by Accounting, default is 
                             -AS
        """
        if not kwargs.has_key('csv_file'):
            raise ValueError("FundBot requires a csv_file")
        self.input_csv = csv.reader(kwargs.get('csv_file'))
        if kwargs.has_key('code_location'):
            self.code_location = int(kwargs.get('code_location'))
        else:
            self.code_location = 9
        if kwargs.has_key('program_code'):
            self.program_code = kwargs.get('program_code')
        else:
            self.program_code = '-AS'
        self.substitutions = 0
        self.amount_re = re.compile(r"\d+[.]\d+")
        self.date_re = re.compile(r"\d+[-]\d+[-]\d+")

    
    def process(self,response):
        """
        Iterates through csv file, replacing each occurrence of fund code 
        with the expanded fund account value.
        
        :param response: Django response object 
        :rtype: file object
        """
        output_csv = csv.writer(response)
        for row in self.input_csv:
            paid_date = row[0]
            invoice_number = row[2]
            invoice_amount = row[3]
            end_index = len(row)-1 
            vendor = row[end_index].strip().upper()
            fund_code = row[end_index-1].strip().upper()
            query = Fund.objects.filter(code=fund_code)
            if query:
                fund_value = "%s%s" % (query[0].value,self.program_code)      
            elif fund_code.startswith('FUND'):
                fund_value = "%s%s" % (fund_code,self.program_code) 
            else:
                fund_value = '%s not found' % fund_code
            # Handles multiple records in a single row for Literature crit online
            if len(row) > 25:                 
                invoice_amount = float(invoice_amount)
                for field in row[4:]:
                    if self.amount_re.search(field):
                        invoice_amount += float(field)
                invoice_amount = '%.2f' % invoice_amount
            # Handles merged records by breaking out the second record info 
            elif len(row) > 11:
                # Assume the second record paid date
                second_paid_date = row[8]
                second_invoice_number = row[10]
                second_invoice_amount = row[11]
                output_csv.writerow([second_paid_date,
                                     second_invoice_number,
                                     second_invoice_amount,
                                     vendor,
                                     fund_value])
            self.substitutions += 1
            output_csv.writerow([paid_date,
                                 invoice_number,
                                 invoice_amount,
                                 vendor,
                                 fund_value])
        return response 
        


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

    def callnumber(self):
        """
        Retrieves call number from XML by first checking to see if there is a 
        090 and then tries 099 field.

        :rtype: string or None
        """
        call_number = '' 
        if self.item_xml is not None:
            # First tries to retrieve 090
            xpath_result = self.item_xml.node.xpath("/IIIRECORD/VARFLD[MARCINFO/MARCTAG[.='090']]/MARCSUBFLD")
            if len(xpath_result) > 0:
                call_number = '' 
                for row in xpath_result:
                    for subfield in row.getchildren():
                        if subfield.tag == 'SUBFIELDDATA':
                            call_number += subfield.text
            # Now tries to retrieve 099
            if len(call_number) < 1:
                xpath_result = self.item_xml.node.xpath("/IIIRECORD/VARFLD[MARCINFO/MARCTAG[.='099']]/MARCSUBFLD[SUBFIELDINDICATOR[.='a']]")
                if len(xpath_result) > 0:
                    for row in xpath_result:
                        for subfield in row.getchildren():
                            
                            if subfield.tag == 'SUBFIELDDATA':
                                call_number += ' %s' % subfield.text
            # Finally tries to retieve 086 for Government Documents
            if call_number is None:
                xpath_result = self.item_xml.node.xpath("/IIIRECORD/VARFLD[MARCINFO/MARCTAG[.='086']]/MARCSUBFLD[SUBFIELDINDICATOR[.='a']]/SUBFIELDDATA")
                if len(xpath_result) > 0:
                    call_number = xpath_result[0].text
      
        return call_number  

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
                return self.item_xml.volume
        return None
            

class PatronBot(object):
    """
    `PatronBot` connects to the III server with the Patron API, parses results 
    and authenticates a user.
    """

    def __init__(self,**kwargs):
        """
        :param last_name: The patron's last name
        :param iii_id: The patron's number
        """
        if kwargs.has_key('last_name'):
            self.last_name = kwargs.get('last_name')
        else:
            raise ValueError('PatronBot requires a last name')
        if kwargs.has_key('iii_id'):
            self.iii_id = kwargs.get('iii_id')
        else:
            raise ValueError('PatronBot requires a last name')
        raw_html = urllib2.urlopen(ILS_PATRON_URL % self.iii_id).read()
        if re.search(r'ERRMSG=',raw_html):
            logging.error("INVALID SEARCH %s" % raw_html)
            self.is_valid = False
        else:
            logging.error("VALID SEARCH")
            self.is_valid = True

"""
 opbots.py - Oxford Press Bots
"""
from marcbots import MARCImportBot

HANDBOOK_PROXY_FILTER = 'http://0-www.oxfordhandbooks.com.tiger.coloradocollege.edu/'
REFERENCE_PROXY_FILTER = 'http://0-www.oxfordreference.com.tiger.coloradocollege.edu/'

class OxfordHandbooksOnlineBot(MARCImportBot):
    """
    Class reads Oxford Handbooks Online MARC records, validates,
    and adds/modifies fields of each MARC record for importing into
    TIGER iii ILS. 
    """

    def __init__(self,**kwargs):
        """
        Initializes `OxfordHandbooksOnlineBot` 
 
        Parameters:
        `marc_file`: Required input MARC file object from Oxford Handbooks
        `proxy_filter`: Optional, proxy prefix for 856 field default is HANDBOOK_PROXY_FILTER
                        constant.
        `public_note`: Optional, default is 'View Online'
        `note_prefix`: Optional 538 note prefix, default is 'Available via Internet'
        `type_of`: Optional, used when specific collections are loaded, used for XXX
                        field.
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError('OxfordHandbooksOnlineBot requires a marc_file object')
        marc_file = kwargs.get('marc_file')
        MARCImportBot.__init__(self,marc_file,output_file)
        if kwargs.has_key('proxy_filter'):
            self.proxy_filter = kwargs.get('proxy_filter')
        else:
            self.proxy_filter = HANDBOOK_PROXY_FILTER
        if kwargs.has_key('public_note'):
            self.public_note = kwargs.get('public_note')
        else:
            self.public_note = 'View online'
        if kwargs.has_key('note_prefix'):
            self.note_prefix = kwargs.get('note_prefix')
        else:
            self.note_prefix='Available via Internet'
        if kwargs.has_key('type_of'):
            self.handbook_type = kwargs.get('type_of')
        else:
            self.handbook_type = None


    def processRecord(self,marc_record):
        """
        Method process record and is called by `MARCImportBot` load method.

        Parameters:
        `marc_record`: Required input MARC file from Oxford Reference, should have been set when instance was initialized.
        """
        #marc_record.leader = self.processLeader(marc_record.leader)
        marc_record = self.remove050(marc_record)
        marc_record = self.remove082(marc_record)
        marc_record = self.validate007(marc_record)
        marc_record = self.validate300(marc_record)
        marc_record = self.remove490(marc_record)
        marc_record = self.remove530(marc_record)
        marc_record = self.validate730(marc_record)
        marc_record = self.remove830(marc_record)
        marc_record = self.processOxfordHandbookURLS(marc_record)
        return marc_record

    def processOxfordHandbookURLS(self,marc_record):
        """
        Method overrides parent processURLS for Oxford Handbook URL  specific
        modification of the 538 and 856 fields

         Parameters:
         `marc_record`: Required, MARC record
        """
        all856fields = marc_record.get_fields('856')
        field856 = all856fields[0]
        # Remove existing 856 fields
        for field in all856fields:
            marc_record.remove_field(field)
        doi_url = field856.get_subfields('u')[0]
        # Retrieve DOI link (redirects to Oxford Handbook URL)
        doi_request = urllib2.urlopen(doi_url)
        ohb_url = doi_request.geturl()
        ohb_path = urlparse.urlsplit(ohb_url).path
        # Create new 538 field
        new538 = Field(tag='538',
                       indicators=[" "," "],
                       subfields=['a','%s, %s' % (self.note_prefix,ohb_url)])
        marc_record.add_field(new538)
        # Create new 856 field
        new856 = Field(tag='856',
                       indicators=['4','0'],
                       subfields=['u','%s%s' % (self.proxy_filter,
                                                ohb_path),
                                  'z',self.public_note])
        marc_record.add_field(new856)
        return marc_record

    def remove082(self,marc_record):
        """
        Removes the 082 field.

        Parameters:
        `marc_record`: Required, MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='082')


    def remove490(self,marc_record):
        """
        Method removes the 490 field.

        Parameters:
        `marc_record`: Required, MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='490')

    def remove830(self,marc_record):
        """
        Method removes the 830 field.

        Parameters:
        `marc_record`: Required, MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='830')


    def validate007(self,marc_record):
        """
        Method validates 007 field, sets position 13 to u
        
        Parameter:
        `marc_record`: Required, MARC record
        """
        field007 = marc_record.get_fields('007')[0]
        org_data = field007.data
        marc_record.remove_field(field007)
        if org_data[13] != 'u':
            org_data = org_data[:13] + r'u'
        field007.data = org_data
        marc_record.add_field(field007)
        return marc_record

    def validate730(self,marc_record):
        """
        Method creates two 730 fields with specific collection set for subfield 
        a.

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='730')
        first730 = Field(tag='730',
                         indicators=['0',' '],
                         subfields=['a','Oxford handbooks online.'])
        marc_record.add_field(first730)
        if self.handbook_type:
            new730 = Field(tag='730',
                           indicators=['0',' '],
                           subfields=['a',self.handbook_type])
            marc_record.add_field(new730)
        return marc_record
class OxfordReferenceOnlineBot(MARCImportBot):
    """
    Class reads Oxford Reference Online MARC file, validates,
    and adds/modifies fields to a new import MARC record for importing
    into TIGER iii ILS.
 
    """

    def __init__(self,**kwargs):
        """
        Initializes `OxfordReferenceOnlineBot`

        Parameters:
        `marc_file`: Required input MARC file from Oxford Reference
        `proxy_filter`: Optional, proxy prefix for 856 field default is REFERENCE_PROXY_FILTER constant.
        `series_title`: Optional, default is 'Oxford reference online premium'
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError("OxfordReferenceOnlineBot requires a marc_file")
        marc_file = kwargs.get('marc_file')
        MARCImportBot.__init__(self,marc_file)
        if kwargs.has_key('proxy_filter'):
            self.proxy_filter = kwargs.get('proxy_filter')
        else:
            self.proxy_filter = REFERENCE_PROXY_FILTER
        if kwargs.has_key('series_title'):
            self.series_title = kwargs.get('series_title')
        else:
            self.series_title = 'Oxford reference online premium'


    def processLeader(self,leader):
        """
        Method processes record leader.

        Parameters:
        `leader`: Required, marc leader
        """
        return leader

    def processRecord(self,marc_record):
        """
        Method process record and is called by `MARCImportBot` load method.

        Parameters:
        `marc_record`: Required input MARC file from Oxford Reference, should
        have been set when instance was initialized.
        """
        marc_record.leader = self.processLeader(marc_record.leader)
        marc_record = self.validate001(marc_record)
        marc_record = self.remove050(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.validate007(marc_record)
        marc_record = self.validate020(marc_record)
        marc_record = self.validate245(marc_record)
        marc_record = self.validate300(marc_record)
        marc_record = self.validate490(marc_record)
        marc_record = self.remove530(marc_record)
        marc_record = self.remove730(marc_record)
        marc_record = self.validate830(marc_record)
        marc_record = self.processURLs(marc_record,self.proxy_filter)
        return marc_record

    def remove730(self,marc_record):
        """
        Method removes all 730 fields in MARC record
       
        Parameters:
        `marc_record`: Required, MARC record
        """
        all730s = marc_record.get_fields('730')
        for field in all730s:
            marc_record.remove_field(field)
        return marc_record


    def validate001(self,marc_record):
        """
        Method validates 001 field, sets control number to OXO
        
        Parameters:
        `marc_record`: Required, MARC record
        """
        field001 = marc_record.get_fields('001')[0]
        org_data = field001.data
        marc_record.remove_field(field001)
        if org_data.find('OROUK') > -1:
            new_data = org_data.replace('OROUK',r'OXO ')
        else:
            new_data = r'OXO %s' % org_data
        field001.data = new_data
        marc_record.add_field(field001)
        return marc_record

    def validate006(self,
                    marc_record):
        """
        Method validates/adds 006 field

        Paramaters:
        - `marc_record`: MARC Record
        """
        all006s = marc_record.get_fields('006')
        if all006s:
            pass
        else:
            field006 = Field(tag='006',indicators=None)
            field006.data = r'm        d        '
            marc_record.add_field(field006)
        return marc_record

    def validate007(self,marc_record):
        """
        Method validates 007 field, sets position 13 to u
        
        Parameter:
        `marc_record`: Required, MARC record
        """
        all007s = marc_record.get_fields('007')
        if len(all007s) > 0:
            field007 = marc_record.get_fields('007')[0]
            org_data = field007.data
            marc_record.remove_field(field007)
            if org_data[13] != 'u':
                org_data = org_data[:13] + r'u'
            field007.data = org_data
            marc_record.add_field(field007)
        else:
            marc_record = self.replace007(marc_record)
        return marc_record

    def validate020(self,marc_record):
        """
        Method checks for any existing 020 records, removes
        any subfield a, adds subfield z with subfield a's value.

        Parameters:
        `marc_record`: Required, MARC record
        """
        all020s = marc_record.get_fields('020')
        for field in all020s:
            subfld_a = field.get_subfields('a')[0]
            marc_record.remove_field(field)
            field.delete_subfield('a')
            field.add_subfield('z',subfld_a)
            marc_record.add_field(field)
        return marc_record

    def validate490(self,marc_record):
        """
        Method checks for any existing 490 records, creates new
        490 record using series_title if 490 field does not exist.

        Parameters:
        `marc_record`: Required, MARC record
        """
        all490s = marc_record.get_fields('490')
        if len(all490s) < 1:
            new490 = Field(tag='490',
                           indicators = ['1',' '],
                           subfields = ['a',self.series_title])
            marc_record.add_field(new490)
        return marc_record

    def validate830(self,marc_record):
        """
        Method removes any existing 830 records, creates new
        830 record using series_title.

        Parameters:
        `marc_record`: Required, MARC record
        """
        all830s = marc_record.get_fields('830')
        for field in all830s:
            marc_record.remove_field(field)
        new830 = Field(tag='830',
                       indicators = [' ','0'],
                       subfields = ['a',self.series_title])
        marc_record.add_field(new830)
        return marc_record



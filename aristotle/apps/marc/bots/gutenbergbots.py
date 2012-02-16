"""
 gutenbergbots.py -- Bot for Project Gutenberg MARC records
"""
__author__ = 'Jeremy Nelson'
from marcbots import MARCImportBot
import re

CONTROL_CODE = 'COC'

class ProjectGutenbergBot(MARCImportBot):
    """
    Class reads Project Gutenberg MARC file, validates, and
    adds/modifies/removes fields to a new import MARC record
    for the TIGER iii database.
    """
    def __init__(self,**kwargs):
        """
        Inititalizes instance of `ProjectGutenbergBot`.

        :param marc_file: Required, MARC record file.
        :param control_code: Optional 003 field value, default is CONTROL_CODE constant
        """
        marc_file = kwargs.get('marc_file')
        if not kwargs.has_key('control_code'):
            self.control_code = CONTROL_CODE
        else:
            self.control_code = kwargs.get('control_code')
        self.url = None
        self.field500_re = re.compile(r"ISO ")
        MARCImportBot.__init__(self,marc_file)

    def processRecord(self,marc_record):
        """
        Method is called by base class load method and processes
        Project Gutenberg MARC record for CC specific manipulation.
        
        :param marc_record: MARC record, required
        """
        marc_record = self.validate003(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.validate007(marc_record)
        marc_record = self.remove042(marc_record)
        marc_record = self.validate245(marc_record)
        marc_record = self.validate300(marc_record)
        marc_record = self.remove500(marc_record)
        marc_record = self.validateURLs(marc_record)
        marc_record = self.remove540(marc_record)
        marc_record = self.validate001(marc_record)
        marc_record = self.validate710(marc_record)
        return marc_record

    def remove042(self,marc_record):
        """
        Removes 042 MARC field
        
        :param marc_record: MARC record, required
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='042')
        return marc_record

    def remove500(self,marc_record):
        """
        Removes 500 field with ISO language code
        
        :param marc_record: MARC record, required
        """
        all_500s = marc_record.get_fields('500')
        for field in all_500s:
            subfield_a = field.get_subfields('a')[0]
            if self.field500_re.search(subfield_a):
                marc_record.remove_field(field)
        return marc_record

    def remove540(self,marc_record):
        """
        Removes 540 MARC field

        :param marc_record: MARC record, required
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='540')
        return marc_record


    def validate001(self,marc_record):
        """
        Method checks/adds 001 field. Control number is 
        derived from 856 URL base value.

        :param marc_record: MARC record, required
        """
        if not self.url:
            raise ValueError('ProjectGutenbergBot.validate001 requires a URL')
        control_number = os.path.basename(self.url)
        self.__remove_field__(marc_record=marc_record,tag='001')
        field001 = Field(tag='001',indicators=None)
        field001.data = r'%s%s' % ('GTB',control_number.rjust(9,'0'))
        marc_record.add_field(field001)
        return marc_record


    def validate003(self,marc_record):
        """
        Validates 003 field, adds control code.

        :param marc_record: MARC record, required
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='003')
        new003 = Field(tag='003',data=self.control_code)
        marc_record.add_field(new003)
        return marc_record

    def validate245(self,marc_record):
        """
        Validates MARC 245 field.

        :param marc_record: MARC record, required
        """
        field245 = marc_record.get_fields('245')[0]
        subfield_a = field245.get_subfields('a')[0]
        allsubfield_b = field245.get_subfields('b')
        indicator1,indicator2 = field245.indicators
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='245')
        if subfield_a.upper().startswith('A '):
            indicator2 = '2'
        elif subfield_a.upper().startswith('AN '):
            indicator2 = '3'
        elif subfield_a.upper().startswith('THE '):
            indicator2 = '4'
        else:
            indicator2 = '0'
        new245 = Field(tag='245',
                       indicators=[indicator1,indicator2],
                       subfields=['a',subfield_a,
                                  'h','[electronic resource] : '])
        if len(allsubfield_b) > 0:
            new245.add_subfield('b',allsubfield_b[0])
        # Extract author name from 700 for subfield c
        all700s = marc_record.get_fields('700')
        if len(all700s) > 0:
            field700 = all700s[0]
        else:
            field700 = None
        if field700:
            raw_name = field700.get_subfields('a')[0]
            final_name = self.__switch_name__(raw_name=raw_name)
            new245.add_subfield('c',final_name)
        marc_record.add_field(new245)
        return marc_record

    def validateURLs(self,marc_record):
        """
        Adds 538 and modifies 856 fields, sets url for
        later validation.

        :param marc_record: MARC record, required
        """
        field856 = marc_record.get_fields('856')[0]
        raw_url = field856.get_subfields('u')[0]
        self.url = raw_url
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='538')
        new538 = Field(tag='538',
                       indicators=[' ',' '],
                       subfields=['a','Available via Internet, %s' % self.url])
        marc_record.add_field(new538)
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='856')
        new856 = Field(tag='856',
                       indicators=['4','1'],
                       subfields=['z','View online',
                                  'u',self.url])
        marc_record.add_field(new856)
        return marc_record


    def validate710(self,marc_record):
        """
        Method validates MARC 710 field

        :param marc_record: MARC record, required
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='710')
        new710field = Field(tag='710',
                            indicators=['2',' '],
                            subfields=['a','Project Gutenberg'])
        marc_record.add_field(new710field)
        return marc_record


"""
 galebots.py - MARC record utilities for Gale Publishing files
"""
__author__ = 'Jeremy Nelson'

from marcbots import MARCImportBot
from pymarc import Field

PROXY_LOCATION='0-find.galegroup.com.tiger.coloradocollege.edu'

class GVRLBot(MARCImportBot):
    ''' Class reads Gale Virtual Reference MARC file, validates, and
        adds/modifies fields to a new import MARC record for importing
        into TIGER iii database.'''

    def __init__(self,
                 marc_file):
        ''' 
        Initializes instance.

        :param marc_file: file location of MARC file.
        '''
        MARCImportBot.__init__(self,marc_file)
        self.stats['titles'] = 0
        self.series_statement = 'Gale virtual reference library'
        self.firm_name = 'Thomson Gale (Firm)'

    def processRecord(self,
                      marc_record):
        ''' 
        Method iterates through specific MARC record and performs validation
        and updates to MARC record before writing to output MARC file.

        :param marc_record:  MARC record, required
        '''
        # Validate 490 and 830 fields
        if not marc_record.get_fields('490','830'):
            marc_record.add_field(Field(tag='490',
                                        indicators=['1','\\'],
                                        subfields=[
                                            'a',self.series_statement]))
            marc_record.add_field(Field(tag='830',
                                        indicators=['\\','0'],
                                        subfields=[
                                            'a',self.series_statement]))
        else:
            marc_record = self.validate490(marc_record)
        # Check for 710 Corporate Name
        if not marc_record.get_fields('710'):
            marc_record.add_field(Field(tag='710',
                                        indicators=['2','\\'],
                                        subfields=['a',
                                                   self.firm_name]))
        else:
            marc_record = self.validate710(marc_record)
        # Replace 538 Systems Record and 856 Electronic Location and Access
        # following standard practice
        marc_record = self.processURLs(marc_record,
                                       proxy_location=PROXY_LOCATION)
        return marc_record

    def validate490(self,marc_record):
        ''' 
        Method validates or sets MARC 490 series statement field and
        corresponding 830 MARC field.

        :param marc_record:  MARC record, required
 
        '''
        field490s = marc_record.get_fields('490')
        field830s = marc_record.get_fields('830')
        if len(field490s) > 0:
            field490 = field490s[0]
            marc_record.remove_field(field490)
            if field490.get_subfields('a')[0] != self.series_statement:
                field490.delete_subfield('a')
                field490.add_subfield('a',self.series_statement)
            field490.indicators = None
            field490.indicators = ['1','\\']
        else:
            field490 = Field(tag='490',
                             indicators=['1','\\'],
                             subfields=['a',self.series_statement])
        if len(field830s) > 0:
            field830 = field830s[0]
            marc_record.remove_field(field830)
            if field830.get_subfields('a')[0] != self.series_statement:
                field830.delete_subfield('a')
                field830.add_subfield('a',self.series_statement)
            field830.indicators = ['\\','0']
        else:
            field830 = Field(tag='830',
                             indicators=['\\','0'],
                             subfields=['a',self.series_statement])
        marc_record.add_field(field490)
        marc_record.add_field(field830)
        return marc_record

    def validate710(self,marc_record): 
        ''' 
        Method validates or sets MARC 710 - Corporate Name field.

        :param marc_record:  MARC record, required
        ''' 
        field710 = marc_record.get_fields('710')[0]  
        if not field710: 
            marc_record.add_field(Field(tag='710', 
                                        indicators = ['2','\\'], 
                                        subfields = [ 
                                            'a',self.firm_name])) 
        else: 
            marc_record.remove_field(field710) 
            if field710.get_subfields('a')[0] != self.firm_name: 
                field710.delete_subfield('a') 
                field710.add_subfield('a',self.firm_name) 
            marc_record.add_field(field710) 
        return marc_record

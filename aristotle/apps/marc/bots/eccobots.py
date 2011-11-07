"""
  eccobots.py - MARC Bots for ECCO MARC files
"""
__author__ = 'Jeremy Nelson'

from marcbots import MARCImportBot

PROXY_LOCATION = '0-galenet.galegroup.com.tiger.coloradocollege.edu'

class ECCOBot(MARCImportBot):
    ''' Class reads Eighteenth Century Collections Online (ECCO) MARC file,
        validates and adds/modifies fields, and generates a MARC file for
        importing into TIGER.'''

    def __init__(self,
                 marc_file):
        ''' 
        Creates instance of bot for creating valid MARC record for
        importing into TIGER from ECCO MARC file.

        :param marc_file:file location for ECCO MARC file
        '''
        self.series_statement = 'Eighteenth century collections online'
        MARCImportBot.__init__(self,marc_file)

    def processRecord(self,marc_record):
        '''
        Call-back method for specific Gale ECCO validation and
        processing.
        
        :param marc_record: MARC record, required
        '''
        marc_record = self.validate001(marc_record)
        marc_record = self.validate490(marc_record)
        marc_record = self.validate830(marc_record)
        marc_record = self.processURLs(marc_record,
                                       proxy_location=PROXY_LOCATION)
        return marc_record

    def validate001(self,marc_record):
        ''' Method sets 001 Control Number of CC's format.

         :param marc_record: MARC record, required
            args:
            marc_record -- MARC record
        '''
        field001 = marc_record.get_fields('001')[0]
        marc_record.remove_field(field001)
        raw_data = field001.data
        field001.data = 'ESTC%s' % raw_data
        marc_record.add_field(field001)
        return marc_record

    def validate490(self,marc_record):
        """
        Method adds/sets 490 field with series statement.

        :param marc_record: MARC record, required
        """
        all490s = marc_record.get_fields('490')
        if len(all490s) > 0:
            for field in all490s:
                marc_record.remove_field(field)
                if field.get_subfields('a')[0] != self.series_statement:
                    field.delete_subfield('a')
                    field.add_subfield('a',self.series_statement)
                field.indicators = None
                field.indicators = ['1','\\']
                marc_record.add_field(field)
        else:
            field490 = Field(tag='490',
                             indicators=['1','\\'],
                             subfields=['a',self.series_statement])
            marc_record.add_field(field490)
        return marc_record

    def validate830(self,marc_record):
        """
        Method adds/sets 830 field with series statement.

        Parameters:
        - `marc_record`: MARC record        
        """
        all830s = marc_record.get_fields('830')
        if len(all830s) > 0:
            for field830 in all830s:
                marc_record.remove_field(field830)
                if field830.get_subfields('a')[0] != self.series_statement:
                    field830.delete_subfield('a')
                field830.add_subfield('a',self.series_statement)
                field830.indicators = ['\\','0']
                marc_record.add_field(field830)
        else:
            field830 = Field(tag='830',
                             indicators=['\\','0'],
                             subfields=['a',self.series_statement])
            marc_record.add_field(field830)
        return marc_record

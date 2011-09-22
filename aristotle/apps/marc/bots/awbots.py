"""
 awbots.py - American West Bots for automating American West MARC record loads
"""
__author__ = 'Jeremy Nelson'

from marcbots import MARCImportBot

PROXY_LOCATION='0-www.americanwest.amdigital.co.uk.tiger.coloradocollege.edu'

class AmericanWestBot(MARCImportBot):
    """
    The `AmericanWestBot` reads MARC records from
    American West Database, validates adds/modify fields
    for a new import MARC file for loading into TIGER
    """
    __name__ = 'American West Bot'

    def __init__(self,
                 marc_file):
        """
        Initializes `AmericanWestBot` for conversion
        process.

        Parameters:
        - `marc_file`: MARC file
        """
        MARCImportBot.__init__(self,marc_file)

    def processRecord(self,
                      marc_record):
        """
        Method processes a single marc_record for American West
        MARC.

        Parameters:
        - `marc_record`: MARC record
        """
        marc_record = self.validate001(marc_record)
        marc_record = self.validate003(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.replace007(marc_record)
        marc_record = self.validate490(marc_record)
        marc_record = self.processURLs(marc_record,
                                       proxy_location=PROXY_LOCATION)
        marc_record = self.validate710(marc_record)
        marc_record = self.validate730(marc_record)
        marc_record = self.validate830(marc_record)
        return marc_record


    def validate001(self,marc_record):
        """
        Method replaces AC prefix with AMP prefix for Prospector compatibility.

        Parameters:
        - `marc_record`: MARC record
        """
        field001 = marc_record.get_fields('001')[0]
        marc_record.remove_field(field001)
        raw_data = field001.data
        field001.data = raw_data.replace('AC','AMP')
        marc_record.add_field(field001)
        return marc_record

    def validate003(self,marc_record):
        """
        Validates 003 field, adds control code.

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='003')
        new003 = Field(tag='003',
                       data='COC')
        marc_record.add_field(new003)
        return marc_record



    def validate490(self,marc_record):
        """
        Method removes all existing 490 fields.

        Parameters:
        - `marc_record`: MARC record
        """
        all490s = marc_record.get_fields('490')
        for field in all490s:
            marc_record.remove_field(field)
        return marc_record

    def validate710(self,
                    marc_record):
        """
        Method validates/adds 710 fields

        Paramaters:
        - `marc_record`: MARC Record
        """
        all710s = marc_record.get_fields('710')
        for field in all710s:
            marc_record.remove_field(field)
        first710 = Field(tag='710',
                       indicators=['2',' '],
                       subfields=['a','Newberry Library.'])
        marc_record.add_field(first710)

        new710 = Field(tag='710',
                       indicators=['2',' '],
                       subfields=['a','Adam Matthew Digital (Firm)'])
        marc_record.add_field(new710)
        return marc_record


    def validate730(self,marc_record):
        """
        Method validates 730 with American West desired text.

        Parameters:
        - `marc_record`: MARC record
        """ 
        self.__remove_field__(marc_record=marc_record,
                              tag='730')
        field730 = Field(tag='730',
                         indicators=['0',' '],
                         subfields=['a','American West (Online Publications)'])
        marc_record.add_field(field730)
        return marc_record

    def validate830(self,marc_record):
        """
        Method removes all existing 830 fields.

        Parameters:
        - `marc_record`: MARC record
        """
        all830s = marc_record.get_fields('830')
        for field in all830s:
            marc_record.remove_field(field)
        return marc_record

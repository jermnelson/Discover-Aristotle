#
# video_bots.py
#
# Colorado College Cataloging utilities
#
__author__ = "Cindy Tappan"
import urlparse,urllib2,re
import datetime,logging
from marcbots import MARCImportBot
from  pymarc import Field

class FilmsOnDemand(MARCImportBot):
    """
    The `FilmsOnDemand` reads MARC records from Films
    on Demand Database,
    validates adds/modify fields for a new import MARC file for loading
    into TIGER. This Bot does not sort fields because MARC ordering is specific
    in video records.
    """

    def __init__(self,
                 marc_file,
                 output_file='vod-%s.mrc'):
        """
        Initializes `FilmsOnDemand` for conversion
        process.

        :param marc_file: MARC file
        :param output_file: Output file name, default is vod-{time-stamp}.mrc
                            used for command-line interface
        """
        MARCImportBot.__init__(self,marc_file,output_file)

    def load(self):
        """
        Load method overrides parent method to preserve ordering of
        5xx fields.
        """
        for record in self.marc_reader:
            if record is None:
                break
            raw_record = self.processRecord(record)
            raw_record = self.remove009(raw_record)
            raw_record = self.remove648(raw_record)
            list001_499 = []
            for num in range(1,500):
                tag = "%03d" % num
                fields = raw_record.get_fields(tag)
                if len(fields)>0:
                    list001_499.extend(fields)
                    for field in fields:
                        raw_record.remove_field(field)
            list600_999 = []
            for num in range(600,1001):
                tag = "%03d" % num
                fields = raw_record.get_fields(tag)
                if len(fields)>0:
                    list600_999.extend(fields)
                    for field in fields:
                        raw_record.remove_field(field)
            list001_499.sort(key=lambda x: x.tag)
            list600_999.sort(key=lambda x: x.tag)
            raw_record.fields = list001_499 + raw_record.fields + list600_999
            self.records.append(raw_record)
   
            self.stats['records'] += 1

    def processRecord(self,marc_record):
        """
        Method processes a single marc_record for Films on Demand MARC.

        :param marc_record: MARC record, required

        """
        marc_record = self.validate001(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.remove020(marc_record)
        marc_record = self.validate245(marc_record)
        marc_record = self.validate300(marc_record)
        marc_record = self.remove490(marc_record)
        marc_record = self.processURLs(marc_record,
                                       proxy_location="0-digital.films.com.tiger.coloradocollege.edu",
                                       public_note='Watch online')
        marc_record = self.validateAll5xxs(marc_record)
        marc_record = self.validate730(marc_record)
        marc_record = self.remove830(marc_record)
        return marc_record
        
    def validate001(self,marc_record):
        """
        Method constructs 001 by inserting fod infront of unique
        number from record provided by FOD.

        :param marc_record: MARC record, required
        """
        field001 = marc_record.get_fields('001')[0]
        marc_record.remove_field(field001)
        raw_data = field001.data 
        new_data = 'fod%s' % raw_data
        field001.data = new_data
        marc_record.add_field(field001)
        return marc_record

    def validate006(self,marc_record):
        """
        Default validation of the 006 field with standard
        field data of m||||||||c|||||||| for electronic video records.

        :param marc_record: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='006')   
        field006 = Field(tag='006',indicators=None)
        field006.data = r'm        c        '
        marc_record.add_field(field006)
        return marc_record

    def replace007(self,marc_record,data=None):
        """
        Removes exisiting 007 fields and replaces with standard data
        for the 007 electronic records.

        :param marc_record: MARC record, required
        :param data: Default data is set if not present, optional
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='007')
        if not data:
            data=r'cr           u'
        new007 = Field(tag='007',data=data)
        marc_record.add_field(new007)
        return marc_record

    def replace007(self,marc_record,data=None):
        """
        Removes exisiting 007 fields and replaces with standard data
        for the 007 electronic records.

        :param marc_record: MARC record
        :param data: Optional, default data is set if not present
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='007')
        if not data:
            data=r'cr           u'
        new007 = Field(tag='007',data=data)
        marc_record.add_field(new007)
        return marc_record

    def remove020(self,marc_record):
        """
        Method removes the 020 field.

        :param marc_record: MARC record, required
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='020')

    def validate300(self,marc_record):
        """
        Method reorders 300 subfield b, removing the word *file*
        
        :param marc_record: MARC record, required
        """
        all300s = marc_record.get_fields('300')
        field300 = all300s[0]
        raw_string = field300.get_subfields('b')[0]
        digital_re = re.compile(r'digital\s?(file)?[.]?')
        good_300b = '%s, %s' % ('digital',digital_re.sub('',raw_string).strip())
        last_char = good_300b[-1]
        if last_char == '+':
             good_300b = good_300b[:-1].strip()
             if good_300b[-1] == ',':
                 good_300b = good_300b[:-1]
             good_300b +=  ' + '
        elif last_char == ',':
            good_300b = good_300b[:-1]
            if good_300b[-1] != '.':
                good_300b = good_300b + '.'
        field300.delete_subfield("b")
        field300.add_subfield("b",good_300b)
        return marc_record

              
    def remove490(self,marc_record):
        """
        Method removes the 490 field.

        :param marc_record: MARC record, required 
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='490')




    def validateAll5xxs(self,marc_record):
        """
        Method orders 5xxs to support streaming video order per AACR2
        538,546,588,511,500s,518,521,520,505,506
        
        :param marc_record: MARC record, required
        """
        all500s = marc_record.get_fields('500')
        all505s = marc_record.get_fields('505')
        all506s = marc_record.get_fields('506')
        all508s = marc_record.get_fields('508')
        all511s = marc_record.get_fields('511')
        all518s = marc_record.get_fields('518')
        all520s = marc_record.get_fields('520')
        all521s = marc_record.get_fields('521')
        all538s = marc_record.get_fields('538')
        all546s = marc_record.get_fields('546')
        all588s = marc_record.get_fields('588')
        self.__remove_field__(marc_record=marc_record,
                                     tag='500')
        self.__remove_field__(marc_record=marc_record,
                                     tag='505')
        self.__remove_field__(marc_record=marc_record,
                                     tag='506')
        self.__remove_field__(marc_record=marc_record,
                                     tag='508')
        self.__remove_field__(marc_record=marc_record,
                                     tag='511')
        self.__remove_field__(marc_record=marc_record,
                                     tag='518')
        self.__remove_field__(marc_record=marc_record,
                                     tag='520')
        self.__remove_field__(marc_record=marc_record,
                                     tag='521')
        self.__remove_field__(marc_record=marc_record,
                                     tag='538')
        self.__remove_field__(marc_record=marc_record,
                                     tag='546')
        self.__remove_field__(marc_record=marc_record,
                                     tag='588')
        
        #starting order of 5xx fields
        for field in all538s:
            marc_record.add_field(field)
        for field in all546s:
            marc_record.add_field(field)
        for field in all588s:
            marc_record.add_field(field)
        for field in all511s:
            marc_record.add_field(field)
        for field in all508s:
            marc_record.add_field(field)
        for field in all500s:
            marc_record.add_field(field)
        for field in all518s:
            marc_record.add_field(field)
        for field in all521s:
            marc_record.add_field(field)
        for field in all520s:
            marc_record.add_field(field)
        for field in all505s:
            marc_record.add_field(field)
        for field in all506s:
            marc_record.add_field(field)
        return marc_record
            

    def validate730(self,marc_record):
        """
        Method removes/replaces existing 730 with uniform title
        for Films on Demand

        :param marc_record: MARC record, required 
        """
        self.__remove_field__(marc_record=marc_record,
                              tag='730')
        field730 = Field(tag='730',
                         indicators=['0',' '],
                         subfields=['a','Films on Demand'])
        marc_record.add_field(field730)
        return marc_record


    def remove830(self,marc_record):
        """
        Method removes the 830 field.

        :param marc_record: MARC record, required 
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='830')


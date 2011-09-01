#
# catalog_bots.py
#
# Colorado College Cataloging utilities
# 
__author__ = 'Jeremy Nelson, Cindy Tappan'
import sys,datetime,logging
import urlparse,urllib2,re
import os
from pymarc import *


class MARCImportBot:
    """ Base class for specific vendor MARC files, children
    classes provide validation methods and methods for adding/
    modifying MARC fields and indicators for importing into
    Colorado College's TIGER iii database.
    """

    def __init__(self,
                 *args):
        if len(args) > 0:
            if __name__ == '__main__':
                self.marc_reader = MARCReader(open(args[0]),
                                              to_unicode=True)
            else:
                self.marc_reader = MARCReader(args[0],
                                              to_unicode=True)
        if len(args) == 2:
            self.marcfile_output = args[1]
        self.records = []
        self.stats = {'records':0}

    def load(self):
        ''' Method iterates through MARC reader, loads specific MARC records
            from reader.
        '''
        for record in self.marc_reader:
            if record is None:
                break
            raw_record = self.processRecord(record)
            # Removes 009, 509, and 648 fields if they exist
            raw_record = self.remove009(raw_record)
            raw_record = self.remove509(raw_record)
            raw_record = self.remove648(raw_record)
            raw_record.fields = sorted(raw_record.fields,key=lambda x: x.tag)
            self.records.append(raw_record)
            self.stats['records'] += 1

    def processRecord(self,marc_record):
        ''' Method should be overriddden by derived classes.'''
        pass

    def processURLs(self,
                    marc_record,
                    proxy_location,
                    public_note='View online',
                    note_prefix='Available via Internet'):
        """ Method extracts URL from 856 field, sets 538 and 856 to CC's format practices.

            Parameters:
            `marc_record` - MARC Record
            `proxy_location` - proxy prefix prepended to extracted URL from 856 field
            `public_note` - subfield z value, default is for CC
            `note_prefix` - prefix for original URL in 538 note field, default is for CC.
        """
        all538fields = marc_record.get_fields('538')
        for field538 in all538fields:
            marc_record.remove_field(field538)
        all856fields = marc_record.get_fields('856')
        for field856 in all856fields:
            # Extracts raw url from 856 subfield u, creates a url object
            # for original and proxy urls and replaces net location with WAM location
            # for proxy
            raw_url = urlparse.urlparse(field856.get_subfields('u')[0])
            if re.match(r'http://',proxy_location):
                protocol = ''
            else:
                protocol = 'http://'
            proxy_raw_url = '%s%s%s?%s' % (protocol,
                                           proxy_location,
                                           raw_url.path,
                                           raw_url.query)
            proxy_url = urlparse.urlparse(proxy_raw_url)
            # Sets values for new 538 with constructed note in     def to_text(self):
            new538 = Field(tag='538',
                           indicators=[' ',' '],
                           subfields=['a','%s, %s' % (note_prefix,raw_url.geturl())])
            marc_record.add_field(new538)
            # Sets values for 856 field
            new856 = Field(tag='856',
                           indicators = ['4','0'],
                           subfields=['u',proxy_url.geturl()])
            # Checks for subfield 3 in original 856 field, adds to public note
            # in subfield z
            new_public_note = public_note
            if len(field856.get_subfields('3')) > 0:
                for subfield3 in field856.get_subfields('3'):
                    subfield3_all = "%s - %s" % (public_note,
                                                 subfield3)
                new_public_note = subfield3_all
            new856.add_subfield('z',new_public_note)
            marc_record.remove_field(field856)
            marc_record.add_field(new856)
        return marc_record    

    def output(self):
        ''' Method writes all records to a MARC21 output file'''
        output = open(self.marcfile_output,'w')
        for record in self.records:
            output.write(record.as_marc())
        output.close()

  

    def remove009(self,marc_record):
        """
        Removes the 009 field, used in some MARC records for local information
        Not used by CC.
        
        Parameters:
        - `marc_record`: MARC record        
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='009')

    def remove050(self,marc_record):
        """
        Removes the 050 field, used in some MARC records for call number.
        
        Parameters:
        - `marc_record`: MARC record        
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='050')

    def remove509(self,marc_record):
        """
        Removes the 509 field, used in some MARC records as a local note.
        Not used by CC.

        Parameters:
        - `marc_record`: MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='509')


    def remove530(self,marc_record):
        """
        Method removes all 530 fields in MARC record
       
        Parameters:
        `marc_record`: Required, MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='530')

    def remove648(self,marc_record):
        """
        Removes the 648 (Chronological Term) from the MARC record
        Not used by CC.
        
        Parameters:
        - `marc_record`: MARC record
        """
        return self.__remove_field__(marc_record=marc_record,
                                    tag='648')

    def replace007(self,marc_record,data=None):
        """
        Removes exisiting 007 fields and replaces with standard data
        for the 007 electronic records.

        Parameters:
        - `marc_record`: MARC record
        - `data`: Optional, default data is set if not present
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='007')
        if not data:
            data=r'cr           u'
        new007 = Field(tag='007',data=data)
        marc_record.add_field(new007)
        return marc_record

    def validate006(self,marc_record):
        """
        Default validation of the 006 field with standard
        field data of m||||||||d|||||||| for electronic records.

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='006')   
        field006 = Field(tag='006',indicators=None)
        field006.data = r'm        d        '
        marc_record.add_field(field006)
        return marc_record

    def validate007(self,marc_record):
        """
        Default validation of the 007 field with the 
        standard CC data of cr|||||||||||u
        
        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.replace007(marc_record)
        return marc_record


    def validate245(self,marc_record):
        """
        Method adds a subfield 'h' with value of electronic resource 
        to the 245 field.

        Parameters:
        `marc_record`: Required, MARC record
        """
        all245s = marc_record.get_fields('245')
        subfield_h_val = '[electronic resource]'
        if len(all245s) > 0:
            field245 = all245s[0]
            marc_record.remove_field(field245)
            subfield_a,subfield_c= '',''
            a_subfields = field245.get_subfields('a')
            indicator1,indicator2 = field245.indicators
            if len(a_subfields) > 0:
                subfield_a = a_subfields[0]
                if subfield_a[-1] == '/':
                    subfield_a = subfield_a[:-1].strip()
            new245 = Field(tag='245',
                           indicators=[indicator1,indicator2],
                           subfields = ['a','%s ' % subfield_a])
            b_subfields = field245.get_subfields('b')
            c_subfields = field245.get_subfields('c')
            if len(c_subfields) > 0 and len(b_subfields) < 1:
                new245.add_subfield('h','%s / ' % subfield_h_val)
            elif len(b_subfields) > 0:
                new245.add_subfield('h','%s : ' % subfield_h_val)
            else:
                new245.add_subfield('h',subfield_h_val)
            if len(b_subfields) > 0:
                for subfield_b in b_subfields:
                    new245.add_subfield('b',subfield_b)
            if len(c_subfields) > 0:
                for subfield_c in c_subfields:
                    new245.add_subfield('c',subfield_c)
            marc_record.add_field(new245)
        return marc_record

    def validate300(self,marc_record):
        """
        Method removes any existing 300 fields, adds a single
        300 field with default of '1 online resource'.

        Parameters:
        `marc_record`: Required, MARC record
        """
        all300s = marc_record.get_fields('300')
        for field in all300s:
            marc_record.remove_field(field)
        new300 = Field(tag='300',
                       indicators=[' ',' '],
                       subfields=['a','1 online resource'])
        marc_record.add_field(new300)
        return marc_record
    
    def validate506(self,marc_record):
        """
        Method removes any existing 506 fields, adds a single
        506 field with default of 'Access limited to subscribers.'

        Parameters:
        `marc_record`: Required, MARC record
        """
        all506s = marc_record.get_fields('506')
        for field in all506s:
            marc_record.remove_field(field)
        new506 = Field(tag='506',
                       indicators=[' ',' '],
                       subfields=['a','Access limited to subscribers.'])
        marc_record.add_field(new506)
        return marc_record

    def to_text(self):
        output_string = r''
        for record in self.records:
            output_string += record.as_marc()
        return output_string

    def __remove_field__(self,**kwargs):
        """
        Internal method removes all instances of a field in
        the MARC record.

        Parameters:
        `marc_record`: Required, MARC record
        `tag`: Required, tag of field 
        """
        if not kwargs.has_key('marc_record') or not kwargs.has_key('tag'):
            raise ValueError('__remove_field__ requires marc_record and tag')
        marc_record,tag = kwargs.get('marc_record'),kwargs.get('tag')
        allfields = marc_record.get_fields(tag)
        for field in allfields:
            marc_record.remove_field(field)
        return marc_record

    def __switch_name__(self,**kwargs):
        """
        Internal method takes a personal name in the format of last_name, 
        first_name middle_names and returns the direct form of the personal
        name.

        Parameters:
        `raw_name`: Required, raw name
        `suffix_list`: Optional, default list is JR., SR., I, II, III, IV
        """
        if not kwargs.has_key('raw_name'):
            ValueError("MARCImportBot.__switch_name__ requires a raw_name")
        raw_name = kwargs.get('raw_name')
        if kwargs.has_key('suffix_list'):
            suffix_list = kwargs.get('suffix_list')
        else:
            suffix_list = ['JR','SR','I','II','III','IV',]
        if raw_name[-1].startswith(","):
            raw_name = raw_name[:-1]
        comma_number = raw_name.find(",")
        if comma_number < 1 or comma_number > 1:
            return raw_name
        last_name,rest_of = raw_name.split(",")
        name_fragments = rest_of.lstrip().split(" ")
        name_fragments = ["%s " % i for i in name_fragments]
        last_position = name_fragments[len(name_fragments)-1].upper().strip()
        def test_suffix(i):
            last_position.startswith(i)
        final_name = ''
        if len(filter(test_suffix,suffix_list)) > 0:
            suffix = name_fragments.pop()
            final_name = ''
            for name in name_fragments:
                final_name += "%s " % name
            final_name += "%s %s" % (last_name,suffix)
        else:
            for name in name_fragments:
                final_name += "%s " % name
            final_name += last_name
        return final_name.strip().replace("  "," ")
    
       
class AmericanWestBot(MARCImportBot):
    """
    The `AmericanWestBot` reads MARC records from
    American West Database, validates adds/modify fields
    for a new import MARC file for loading into TIGER
    """

    def __init__(self,
                 marc_file,
                 output_file='asp-%s.mrc'):
        """
        Initializes `AmericanWestBot` for conversion
        process.

        Parameters:
        - `marc_file`: MARC file
        - `output_file`: Output file name, default is asp-{time-stampe}.mrc
           used for command-line interface
        """
        MARCImportBot.__init__(self,marc_file,output_file)

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
                                       proxy_location='0-www.americanwest.amdigital.co.uk.tiger.coloradocollege.edu')
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


class ECCOBot(MARCImportBot):
    ''' Class reads Eighteenth Century Collections Online (ECCO) MARC file,
        validates and adds/modifies fields, and generates a MARC file for
        importing into TIGER.'''

    def __init__(self,
                 marc_file,
                 output_file='gale-ecco-%s.mrc' %
                 datetime.datetime.now().strftime("%Y%m%d")):
        ''' Creates instance of bot for creating valid MARC record for
            importing into TIGER from ECCO MARC file.

            args:
            marc_file -- file location for ECCO MARC file
            output_file -- Optional, output MARC file name
        '''
        self.series_statement = 'Eighteenth century collections online'
        MARCImportBot.__init__(self,marc_file,output_file)

    def processRecord(self,marc_record):
        '''Call-back method for specific Gale ECCO validation and
           processing.

           args:
           marc_record -- MARC record
        '''
        marc_record = self.validate001(marc_record)
        marc_record = self.validate490(marc_record)
        marc_record = self.validate830(marc_record)
        marc_record = self.processURLs(marc_record,
                                       proxy_location='0-galenet.galegroup.com.tiger.coloradocollege.edu')
        return marc_record

    def validate001(self,marc_record):
        ''' Method sets 001 Control Number of CC's format.

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

        Parameters:
        - `marc_record`: MARC record
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

class GVRLBot(MARCImportBot):
    ''' Class reads Gale Virtual Reference MARC file, validates, and
        adds/modifies fields to a new import MARC record for importing
        into TIGER iii database.'''

    def __init__(self,
                 marc_file,
                 output_file='gvrl-%s.mrc' % \
                 datetime.datetime.now().strftime("%Y%m%d")):
        ''' Initializes instance.

             args:
             marc_file -- file location of MARC file.
             output_file -- output MARC file name, default is given
                            with current date stamp
        '''
        MARCImportBot.__init__(self,marc_file,output_file)
        self.stats['titles'] = 0
        self.series_statement = 'Gale virtual reference library'
        self.firm_name = 'Thomson Gale (Firm)'
        
    
    def processRecord(self,
                      marc_record):
        ''' Method iterates through specific MARC record and performs validation
            and updates to MARC record before writing to output MARC file.

            args:
            marc_record -- MARC record
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
                                       proxy_location='0-find.galegroup.com.tiger.coloradocollege.edu')
        return marc_record


        
    def validate490(self,marc_record):
        ''' Method validates or sets MARC 490 series statement field and
            corresponding 830 MARC field.'''
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
        ''' Method validates or sets MARC 710 - Corporate Name field.'''
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

class LTISortBot(object):
    """
    Class reads an LTI load file and sorts all fields by number
    and no other validation.
    """
    def __init__(self,**kwargs):
        """
        Initialize `LTISortBot` class.

        Parameters:
        `marc_file`: Required, LTI MARC upload file
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError('LTISortBot requires LTI MARC file')
        lti_file = kwargs.get('marc_file')
        if __name__ == '__main__':
            self.marc_reader = MARCReader(open(lti_file),
                                          to_unicode=True)
        else:
            self.marc_reader = MARCReader(lti_file,
                                          to_unicode=True)
        self.records = []
        self.stats = {'records':0}


    def load(self):
        """
        Method loads and sorts each record in LTI load MARC file
        """
        for record in self.marc_reader:
            self.stats['records'] += 1
            record.fields = sorted(record.fields,key=lambda x: x.tag)
            self.records.append(record)

    def to_text(self):
        """
        Method creates raw string of MARC records
        """
        output_string = r''
        for record in self.records:
            output_string += record.as_marc()
        return output_string
 

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
        `output_file`: Optional, default is oro-YYYYmmdd.mrc
        `proxy_filter`: Optional, proxy prefix for 856 field default is 
                        http://0-www.oxfordhandbooks.com.tiger.coloradocollege.edu/
        `series_title`: Optional, default is 'Oxford reference online premium'
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError("OxfordReferenceOnlineBot requires a marc_file")
        marc_file = kwargs.get('marc_file')
        if kwargs.has_key('output_file'):
            output_file = kwargs.get( 'output_file')
        else:
            output_file = 'oro-%s.mrc' % datetime.datetime.now().strftime("%Y%m%d")
        MARCImportBot.__init__(self,marc_file,output_file)
        if kwargs.has_key('proxy_filter'):
            self.proxy_filter = kwargs.get('proxy_filter')
        else:
            self.proxy_filter = 'http://0-www.oxfordreference.com.tiger.coloradocollege.edu/'
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
        `marc_file`: Required input MARC file from Oxford Handbooks
        `output_file`: Optional, default output file is oho-YYYmmdd.mrc
        `proxy_filter`: Optional, proxy prefix for 856 field default is 
                        http://0-www.oxfordhandbooks.com.tiger.coloradocollege.edu/
        `public_note`: Optional, default is 'View Online'
        `note_prefix`: Optional 538 note prefix, default is 'Available via Internet'
        `type_of`: Optional, used when specific collections are loaded, used for XXX
                        field.
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError('OxfordHandbooksOnlineBot requires a marc_file')
        marc_file = kwargs.get('marc_file')
        if kwargs.has_key('output_file'):
            output_file = kwargs.get('output_file')
        else:
            output_file = 'oho-%s.mrc' % datetime.datetime.now().strftime("%Y%m%d")
        MARCImportBot.__init__(self,marc_file,output_file)
        if kwargs.has_key('proxy_filter'):
            self.proxy_filter = kwargs.get('proxy_filter')
        else:
            self.proxy_filter = 'http://0-www.oxfordhandbooks.com.tiger.coloradocollege.edu/'
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

class ProjectGutenbergBot(MARCImportBot):
    """
    Class reads Project Gutentberg MARC file, validates, and
    adds/modifies/removes fields to a new import MARC record
    for the TIGER iii database.
    """

    def __init__(self,**kwargs):
        """
        Inititalizes instance of `ProjectGutenbergBot`.

        Parameters:
        `marc_file`: Required, MARC record file.
        `output_file`: Optional, default is gtb-YYYYmmdd.mrc
        `control_code`: Optional 003 field value, default is COC
        """
        if not kwargs.has_key('marc_file'):
            raise ValueError("ProjectGutenbergBot requires a marc_file")
        marc_file = kwargs.get('marc_file')
        if not kwargs.has_key('output_file'):
            output_file = 'gtb-%s.mrc' % datetime.datetime.now().strftime("%Y%m%d")
        else:
            output_file = kwargs.get('output_file')
        if not kwargs.has_key('control_code'):
            self.control_code = 'COC'
        else:
            self.control_code = kwargs.get('control_code')
        self.url = None
        self.field500_re = re.compile(r"ISO ")
        MARCImportBot.__init__(self,marc_file,output_file)
       

    def processRecord(self,marc_record):
        """
        Method is called by base class load method and processes
        Project Gutenberg MARC record for CC specific manipulation.
        
        Parameters:
        `marc_record`: Required, MARC record
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
        
        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='042')
        return marc_record

    def remove500(self,marc_record):
        """
        Removes 500 field with ISO language code

        Parameters:
        `marc_record`: Required, MARC record
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

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='540')
        return marc_record


    def validate001(self,marc_record):
        """
        Method checks/adds 001 field. Control number is 
        derived from 856 URL base value.

        Parameters:
        `marc_record`: Required, MARC record
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

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='003')
        new003 = Field(tag='003',data=self.control_code)
        marc_record.add_field(new003)
        return marc_record


    def validate245(self,marc_record):
        """
        Validates MARC 235 field.

        Parameters:
        `marc_record`: Required, MARC record
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

        Paramters:
        `marc_record`: Required, MARC record
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

        Parameters:
        `marc_record`: Required, MARC record
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='710')
        new710field = Field(tag='710',
                            indicators=['2',' '],
                            subfields=['a','Project Gutenberg'])
        marc_record.add_field(new710field)
        return marc_record
        
    
class SpringerEBookBot(MARCImportBot):
    ''' Class reads SpringLink eBook MARC file, validates, and
        adds/modifies fields to a new import MARC record for importing
        into TIGER iii database.'''

    def __init__(self,
                 marc_file,
                 output_file='spr-%s.mrc' % \
                             datetime.datetime.now().strftime("%Y%m%d")):
        ''' Creates instance of Springer eBook process.

            args:
            marc_file -- file location for Spring eBook MARC file
        '''
        MARCImportBot.__init__(self,marc_file,output_file)
        self.spr_url = 'http://www.springerlink.com/openurl.asp?genre=book&id=doi:'
        self.spr_proxy = 'http://0-www.springerlink.com.tiger.coloradocollege.edu/openurl.asp?genre=book&id=doi:'
        self.public_note='View online'
        self.note_prefix='Available via Internet'
                                       


    def processLeader(self,marc_leader):
        ''' Method validates/sets leader positions for Spring MARC record.

            args:
            marc_leader -- MARC file leader
        '''
        # Checks/sets record type in position 6
        if marc_leader[6-1] != 'a':
            marc_leader = marc_leader[0:5] + 'a' + marc_leader[6:]
        # Checks/sets Encoding level in position 17
        if marc_leader[17-1] != 'u':
            marc_leader = marc_leader[0:16] + 'u' + marc_leader[17:]
        return marc_leader


    def processRecord(self,marc_record):
        ''' Call-back method called by base class load method, Springer
            eBook specific validation.

            args:
            marc_record -- MARC record
        '''
        marc_record.leader = self.processLeader(marc_record.leader)
        marc_record = self.validate001(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.validate008(marc_record)        
        marc_record = self.processSpringerURLs(marc_record)        
        return marc_record

    def validate001(self,marc_record):
        ''' Method sets 001 Control Number of CC's format.

            args:
            marc_record -- MARC record
        '''
        field001 = marc_record.get_fields('001')[0]
        marc_record.remove_field(field001)
        raw_data = field001.data
        if raw_data.find('spr') < 0:
            new_data = "spr%s" % raw_data.replace("-","")
        else:
            new_data = raw_data.replace("-","")
        field001.data = new_data
        marc_record.add_field(field001)
        return marc_record

    def validate006(self,marc_record):
        ''' Method checks/sets 006 fixed length data elements in MARC
            record.

            args:
            marc_record -- MARC record
        '''
        existing_fields = marc_record.get_fields('006')
        if existing_fields:
            field006 = existing_fields[0]
            marc_record.remove_field(field006)
        else:
            field006 = Field(tag='006',indicators=None)
        field006.data = r'm        d        '
        marc_record.add_field(field006)
        return marc_record
        

    def validate008(self,marc_record):
        ''' Method checks/sets 008 fixed length data elements in MARC
            record.

            args:
            marc_record -- MARC record
        '''
        field008 = marc_record.get_fields('008')[0]
        marc_record.remove_field(field008)
        # Form of item
        if field008.data[24-1] != 's':
            field008.data = field008.data[0:23] + 's' + field008.data[24:]
        # Nature of content, set to None
        if field008.data[27-1]:
            field008.data = field008.data[0:26] +  r' ' + field008.data[27:]
        marc_record.add_field(field008)
        return marc_record
    
    def processSpringerURLs(self,marc_record):
        '''
         Method overrides parent processURLS for Springer specific
         modification of the 538 and 856 fields

         args:
         marc_record -- MARC record
         '''
        all856fields = marc_record.get_fields('856')
        field856 = all856fields[0]
        for field in all856fields:
            marc_record.remove_field(field)
        raw_url = urlparse.urlparse(field856.get_subfields('u')[0])
        doi = raw_url.path[1:]
        all538fields = marc_record.get_fields('538')
        for field in all538fields:
            marc_record.remove_field(field)
        new856 = Field(tag='856',
                       indicators=['4','0'],
                       subfields=['u','%s%s' % (self.spr_proxy,
                                                doi),
                                  'z',self.public_note])
        marc_record.add_field(new856)
        new538 = Field(tag='538',
                       indicators=[" "," "],
                       subfields=['a','%s,%s%s' % (self.note_prefix,
                                                   self.spr_url,
                                                   doi)])
        marc_record.add_field(new538)
        return marc_record
        


if __name__ == '__main__':
    menu = ['Gale Virtual Reference MARC file validation',
            'SpringerLink eBook MARC file validation',
            'Gale Eighteenth Century Collections Online (ECCO)']
    print("Colorado College Cataloging Utilities Command Line %s" %\
          datetime.datetime.now().ctime())
    print("Please select from the following:")
    for i,v in enumerate(menu):
        print("\t(%s) %s" % (i+1,v))
    raw_prompt = raw_input(">> ")
    try:
        prompt = int(raw_prompt)
    except:
        print("%s not valid" % raw_prompt)
    if prompt == 1:
        print(menu[prompt-1])
        print("Please enter full location of MARC file from Gale below")
        print("(Note: use 2 backslashes for Windows location \\ instead of one")
        print(" example - C:\\Downloads\\gale.mrc)")
        raw_file_location = raw_input(">> ")
        file_object = open(raw_file_location)
        gvrl_utility = GVRLBot(file_object)
        gvrl_utility.load()
        gvrl_utility.output()
        print("Output MARC file %s on %s" % (gvrl_utility.marcfile_output,
                                             datetime.datetime.now().ctime()))
    elif prompt == 2:
        print(menu[prompt-1])
        print("Please enter full location of MARC file from SpringLink below")
        raw_file_location = raw_input(">> ")
        spr_utility = SpringerEBookBot(marc_file=raw_file_location)
        spr_utility.load()
        spr_utility.output()
        print("Output MARC file %s on %s" % (spr_utility.marcfile_output,
                                             datetime.datetime.now().ctime()))
    elif prompt == 3:
        print(menu[prompt-1])
        print("Please enter full location of MARC file from ECCO Gale below")
        raw_file_location = raw_input(">> ")
        ecco_bot = ECCOBot(marc_file=raw_file_location)
        ecco_bot.load()
        ecco_bot.output()
        print("Output MARC file %s on %s" % (ecco_bot.marcfile_output,
                                             datetime.datetime.now().ctime()))
    else:
        print("Unknow selection %s" % prompt)
            

# -*- coding: utf8 -*-

# Copyright 2011 Jeremy Nelson
#
# Copyright 2008 Gabriel Sean Farrell
# Copyright 2008 Mark A. Matienzo
#
# This file is derived from Kochief project.
# 
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

"""Helpers for MARC processing."""

import csv
import pymarc
import re
import sys
import time,datetime
import unicodedata
import urllib
import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import simplejson

logging.basicConfig(filename='%slog/%s-marc-solr-indexer.log' % (settings.BASE_DIR,
                                                                 datetime.datetime.today().strftime('%Y%m%d-%H')),
                    level=logging.INFO)

#logger = logging.getLogger('marc_solr_import')
#logger.setLevel(logging.INFO)
#logger.addHandler(logging.FileHandler('%slog/%s-marc-solr-indexer.out' %\
#                                     (settings.BASE_DIR,
#                                      datetime.datetime.today().strftime('%Y%m%d-%H'))))
#log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


try:
    set
except NameError:
    from sets import Set as set

# local libs
import marc_maps,tutt_maps

NONINT_RE = re.compile(r'\D')
ISBN_RE = re.compile(r'(\b\d{10}\b|\b\d{13}\b)')
UPC_RE = re.compile(r'\b\d{12}\b')
LOCATION_RE = re.compile(r'\(\d+\)')
FIELDNAMES = [
    'access',
    'audience',
    'author',
    'bib_num',
    'callnum',
    'collection',
    'contents',
    'corporate_name',
    'ctrl_num',
    'description',
    'era',
    'format',
    'full_title',
    'full_lc_subject',
    'genre',
    'id',
    'imprint',
    'isbn',
    'item_ids',
    'language',
    'language_dubbed', 
    'language_subtitles',
    'lc_firstletter',
    'location',
    'marc_record',
    'oclc_num',
    'notes',
    'personal_name',
    'place',
    'publisher',
    'publisher_location',
    'pubyear',
    'series',
    'summary',
    'title',
    'title_sort',
    'topic',
    'upc',
    'url',
]

class RowDict(dict):
    """
    Subclass of dict that joins sequences and encodes to utf-8 on get.
    Encoding to utf-8 is necessary for Python's csv library because it 
    can't handle unicode.
    >>> row = RowDict()
    >>> row['bob'] = ['Montalb\\xe2an, Ricardo', 'Roddenberry, Gene']
    >>> row.get('bob')
    'Montalb\\xc3\\xa1n, Ricardo|Roddenberry, Gene'
    >>> print row.get('bob')
    Montalbán, Ricardo|Roddenberry, Gene
    """
    def get(self, key, *args):
        value = dict.get(self, key, *args)
        if not value:
            return ''
        if hasattr(value, '__iter__'):
            value = '|'.join([x for x in value if x])
        # converting to utf8 with yaz-marcdump instead -- it handles
        # oddities better
        return pymarc.marc8.marc8_to_unicode(value).encode('utf8')
        # convert to unicode if value is a string
        #if type(value) == type(''):
        #    value = unicode(value, 'utf8')
        # converting to NFC form lessens character encoding issues 
        value = unicodedata.normalize('NFC', value)
        return value.encode('utf8')

def normalize(value):
    if value:
        return value.replace('.', '').strip(',:/; ')
  
def subfield_list(field, subfield_indicator):
    subfields = field.get_subfields(subfield_indicator)
    if subfields is not None:
        return [normalize(subfield) for subfield in subfields]
    else:
        return []

def multi_field_list(fields, indicators):
    values = []
    for f in fields:
        for i in indicators:
            values.extend(subfield_list(f, i))
    return set(values)

access_search = re.compile(r'ewww')

def get_access(record):
    '''Generates simple access field specific to CC's location codes'''
    if record['994']:
        raw_location = record['994'].value()
        if access_search.search(raw_location):
            return 'Online'
        else:
            return 'In the Library'
    else:
        return 'In the Library'

def get_format(record):
    '''Generates format, extends existing Kochief function.'''
    format = ''
    if record['007']:
        field007 = record['007'].value()
    else:
        field007 = ''
    leader = record.leader
    if len(leader) > 7:
        if len(field007) > 5:
            if field007[0] == 'a':
                if field007[1] == 'd':
                    format = 'Atlas'
                else:
                    format = 'Map'
            elif field007[0] == 'c':            # electronic resource
                if field007[1] == 'j':
                    format = 'Floppy Disk'
                elif field007[1] == 'r':        # remote resource
                    if field007[5] == 'a':    # has sound
                        format = 'Electronic'
                    else:
                        format = 'Electronic'
                elif field007[1] == 'o' or field007[1] == 'm':      # optical disc
                    format = 'CDROM'
            elif field007[0] == 'd':
                format = 'Globe'
            elif field007[0] == 'h':
                format = 'Microfilm'
            elif field007[0] == 'k': # nonprojected graphic
                if field007[1] == 'c':
                    format = 'Collage'
                elif field007[1] == 'd':
                    format = 'Drawing'
                elif field007[1] == 'e':
                    format = 'Painting'
                elif field007[1] == 'f' or field007[1] == 'j':
                    format = 'Print'
                elif field007[1] == 'g':
                    format = 'Photonegative'
                elif field007[1] == 'l':
                    format = 'Drawing'
                elif field007[1] == 'o':
                    format = 'Flash Card'
                elif field007[1] == 'n':
                    format = 'Chart'
                else:
                    format = 'Photo'
            elif field007[0] == 'm': # motion picture
                if field007[1] == 'f':
                    format = 'Videocassette'
                elif field007[1] == 'r':
                    format = 'Filmstrip'
                else:
                    format = 'Motion picture'
            elif field007[0] == 'o': # kit
                format = 'kit'
            elif field007[0] == 'q':
                format = 'musical score'
            elif field007[0] == 's':          # sound recording
                if leader[6] == 'i':             # nonmusical sound recording
                    if field007[1] == 's':   # sound cassette
                        format = 'Book On Cassette'
                    elif field007[1] == 'd':    # sound disc
                        if field007[6] == 'g' or field007[6] == 'z':
                            # 4 3/4 inch or Other size
                            format = 'Book On CD'
                elif leader[6] == 'j':        # musical sound recording
                    if field007[1] == 's':    # sound cassette
                        format = 'Cassette'
                    elif field007[1] == 'd':    # sound disc
                        if field007[6] == 'g' or field007[6] == 'z':
                            # 4 3/4 inch or Other size
                            format = 'Music CD'
                        elif field007[6] == 'e':   # 12 inch
                            format = 'LP Record'
            elif field007[0] == 'v':            # videorecording
                if field007[1] == 'd':        # videodisc
                    if field007[4] == 'v' or field007[4] == 'g':
                        format = 'DVD Video'
                    elif field007[4] == 's':
                        format = 'Blu-ray Video' 
                    elif field007[4] == 'b':
                        format = 'VHS Video' 
                    else:
                        logging.error("247 UNKNOWN field007 %s for %s" % (field007[4],record.title()))
                elif field007[1] == 'f':        # videocassette
                    format = 'VHS Video'
                elif field007[1] == 'r':
                    format = 'Video Reel'
    # now do guesses that are NOT based upon physical description 
    # (physical description is going to be the most reliable indicator, 
    # when it exists...)
    if record['008']:
            field008 = record['008'].value()
    else:
            field008 = ''
    if leader[6] == 'a' and len(format) < 1:                # language material
        if leader[7] == 'c':
            format = 'Collection'
        if leader[7] == 'm':            # monograph
            if len(field008) > 22:
                if field008[23] == 'd':    # form of item = large print
                    format = 'Large Print Book'
                elif field008[23] == 's':    # electronic resource
                    format = 'Electronic'
                else:
                    format = 'Book'
            else:
                format = 'Book'
        elif leader[7] == 's':            # serial
            if len(field008) > 18:
                frequencies = ['b', 'c', 'd', 'e', 'f', 'i', 'j', 
                        'm', 'q', 's', 't', 'w']
                if field008[18] in frequencies:
                    format = 'Journal'
                else:
                    # this is here to prevent stuff that librarians 
                    # and nobody else would consider to be a serial 
                    # from being labeled as a magazine.
                    format = 'Book'
    elif leader[6] == 'b' and len(format) < 1:
        format = 'Music CD'
    elif leader[6] == 'e' and len(format) < 1:
        format = 'Map'
    elif leader[6] == 'c' and len(format) < 1:
        format = 'Musical Score'
    elif leader[6] == 'g' and len(format) < 1:
        format = 'Video'
    elif leader[6] == 'd' and len(format) < 1:
        format = 'Manuscript'
    elif leader[6] == 'j' and len(format) < 1:
        format = 'Music Cassette' 
    elif leader[6] == 'k' and len(format) < 1:
        if len(field008) > 22:
            if field008[33] == 'i':
                format = 'Poster'
            elif field008[33] == 'o':
                format = 'Flash Cards'
            elif field008[33] == 'n':
                format = 'Charts'
    elif leader[6] == 'm' and len(format) < 1:
        format = 'Electronic'
    elif leader[6] == 'p' and len(format) < 1:
        if leader[7] == 'c':
            format = 'Collection'
        else:
            format = 'Mixed Materials'
    elif leader[6] == 'o' and len(format) < 1:
        if len(field008) > 22:
            if field008[33] == 'b':
                format = 'Kit'
    elif leader[6] == 'r' and len(format) < 1:
        if field008[33] == 'g':
            format = 'Games'
    elif leader[6] == 't' and len(format) < 1:
        if len(field008) > 22:
            if field008[24] == 'm':
                format = 'Thesis'
            elif field008[24] == 'b':
                format = 'Book'
            else:
                logging.error("314 Trying re on field 502 for %s" % record.title())
                thesis_re = re.compile(r"Thesis")
                #! Quick hack to check for "Thesis" string in 502
                if record['502']:
                    desc502 = record['502'].value()
                else:
                    desc502 = ''
                if thesis_re.search(desc502):
                    format = 'Thesis'
                else:
                    format = 'Manuscript'
        else:
            format = 'Manuscript'
    # checks 006 to determine if the format is a manuscript
    if record['006'] and len(format) < 1:
        field006 = record['006'].value()
        if field006[0] == 't':
            format = 'Manuscript'
        elif field006[0] == 'm' or field006[6] == 'o':
            #! like to use field006[9] to further break-down Electronic format
            format = 'Electronic'
    # Doesn't match any of the rules
    if len(format) < 1:
        logging.error("309 UNKNOWN FORMAT Title=%s Leader: %s" % (record.title(),leader))
        format = 'Unknown'
    return format

def get_subject_names(record):
    """
     Iterates through record's 600 fields, returns a list of names
 
     Parameters:
     * `record` -- MARC record, required
    """
    output = []
    subject_name_fields = record.get_fields('600')
    for field in subject_name_fields:
        name = field.get_subfields('a')[0]
        titles = field.get_subfields('c')
        for title in titles:
            name = '%s %s' % (title,name)
        numeration = field.get_subfields('b')
        for number in numeration:
            name = '%s %s' % (name,number)
        dates = field.get_subfields('d')
        for date in dates:
            name = '%s %s' % (name,date)
        output.append(name)
    return output

def parse_008(record, marc_record):
    if marc_record['008']:
        field008 = marc_record['008'].value()

        # "a" added for noninteger search to work
        dates = (field008[7:11] + 'a', field008[11:15] + 'a')
        # test for which date is more precise based on searching for
        # first occurence of nonintegers, i.e. 196u > 19uu
        occur0 = NONINT_RE.search(dates[0]).start()
        occur1 = NONINT_RE.search(dates[1]).start()
        # if both are specific to the year, pick the earlier of the two
        if occur0 == 4 and occur1 == 4:
            date = min(dates[0], dates[1])
        else:
            if occur0 >= occur1:
                date = dates[0]
            else:
                date = dates[1]
        # don't use it if it starts with a noninteger
        if NONINT_RE.match(date):
            record['pubyear'] = ''
        else:
            # substitute all nonints with dashes, chop off "a"
            date = NONINT_RE.sub('-', date[:4])
            record['pubyear'] = date
            # maybe try it as a solr.DateField at some point
            #record['pubyear'] = '%s-01-01T00:00:01Z' % date
    
        audience_code = field008[22]
        if audience_code != ' ':
            try:
                record['audience'] = marc_maps.AUDIENCE_CODING_MAP[audience_code]
            except KeyError, error:
                #sys.stderr.write("\nIllegal audience code: %s\n" % error)
                record['audience'] = ''

        language_code = field008[35:38]
        try:
            record['language'] = marc_maps.LANGUAGE_CODING_MAP[language_code]
        except KeyError:
            record['language'] = ''
    return record

def id_match(id_fields, id_re):
    id_list = []
    for field in id_fields:
        id_str = normalize(field['a'])
        if id_str:
            id_match = id_re.match(id_str)
            if id_match:
                id = id_match.group()
                id_list.append(id)
    return id_list

def get_languages(language_codes):
    split_codes = []
    for code in language_codes:
        code = code.lower()
        if len(code) > 3:
            split_code = [code[k:k+3] for k in range(0, len(code), 3)]
            split_codes.extend(split_code)
        else:
            split_codes.append(code)
    languages = []
    for code in split_codes:
        try:
            language = marc_maps.LANGUAGE_CODING_MAP[code]
        except KeyError:
            language = None
        if language:
            languages.append(language)
    return set(languages)


def get_callnumber(record):
    """Follows CC's practice, you may have different priority order
    for your call number."""
    callnumber = ''
    # First check to see if there is a sudoc number
    if record['086']:
        callnumber = record['086'].value()
    # Next check to see if there is a local call number
    elif record['099']:
        callnumber = record['099'].value()
    elif record['090']:
        callnumber = record['090'].value()
    # Finally checks for value in 050
    elif record['050']:
        callnumber = record['050'].value()
    return callnumber

def get_items(record,ils=None):
    """Extracts item id from bib record for web service call
    to active ILS."""
    items = []
    if record["945"]:
        all945s = record.get_fields('945')
        for f945 in all945s:
            for y in f945.get_subfields('y'):
                if ils=='III': # Removes starting period and trailing character 
                    items.append(y[1:-1]) 
    return items  

lc_stub_search = re.compile(r"([A-Z]+)")

def get_lcletter(record):
    '''Extracts LC letters from call number.'''
    lc_descriptions = []
    if record['050']:
        callnum = record['050'].value()
    elif record['945']:
        callnum = record['945'].value()
    else:
        return None
    lc_stub_result = lc_stub_search.search(callnum)
    if lc_stub_result:
        code = lc_stub_result.groups()[0]
        try:
            lc_descriptions.append(marc_maps.LC_CALLNUMBER_MAP[code])
        except:
            pass
    return lc_descriptions

def get_location(record):
    """Uses CC's location codes in Millennium to map physical
    location of the item to human friendly description from 
    the tutt_maps LOCATION_CODE_MAP dict"""
    output = []
    if record['994']:
        locations = record.get_fields('994')
    for row in locations:
        try:
            locations_raw = row.get_subfields('a')
            for code in locations_raw:
                code = LOCATION_RE.sub("",code)
                output.append(tutt_maps.LOCATION_CODE_MAP[code])
        except KeyError:
            logging.info("%s Location unknown=%s" % (record.title(),locations[0].value()))
            output.append('Unknown')
    return set(output)
# Roles with names (i.e. "Glover, Crispin (Actor)") looks neat but is
# kind of useless from a searching point of view.  A search for "Law,
# Jude (Actor)" won't return plain old "Law, Jude".  I welcome other
# ideas for incorporating roles.
#def extract_name(field):
#    role_map = maps.ROLE_CODING_MAP
#    name = normalize(field['a'])
#    if name:
#        role_key = field['4']
#        if role_key:
#            try:
#                name = '%s (%s)' % (name, role_map[role_key])
#            except KeyError:
#                pass
#    return name
        
def generate_records(data_handle):
    reader = pymarc.MARCReader(data_handle)
    for marc_record in reader:
        record = get_record(marc_record)
        if record:  # skip when get_record returns None
            yield record

def get_record(marc_record, ils=None):
    """
    Pulls the fields from a MARCReader record into a dictionary.
    >>> marc_file_handle = open('test/marc.dat')
    >>> reader = pymarc.MARCReader(marc_file_handle)
    >>> for marc_record in reader:
    ...     record = get_record(marc_record)
    ...     print record['author']
    ...     break
    ...
    George, Henry, 1839-1897.
    """
    record = {}

    # TODO: split ILS-specific into separate parsers that subclass this one:
    # horizonmarc, iiimarc, etc.
    try:
        if ils == 'Horizon':
            record['id'] = marc_record['999']['a']
        elif ils == 'III':
            # [1:-1] because that's how it's referred to in the opac
            record['id'] = marc_record['907']['a'][1:-1]
        elif ils == 'Unicorn':
            record['id'] = marc_record['35']['a']
        else:
            # Includes Aleph and Voyager.
            record['id'] = marc_record['001'].value()
    except AttributeError:
        # try other fields for id?
        #sys.stderr.write("\nNo value in ID field, leaving ID blank\n")
        #record['id'] = ''
        # if it has no id let's not include it
        return
    
    record['format'] = get_format(marc_record)

    # should ctrl_num default to 001 or 035?
    if marc_record['001']:
        record['ctrl_num'] = marc_record['001'].value() 

    # there should be a test here for the 001 to start with 'oc'
    try:
        oclc_number = marc_record['001'].value()
    except AttributeError:
        oclc_number = ''
    record['oclc_num'] = oclc_number

    record = parse_008(record, marc_record)

    isbn_fields = marc_record.get_fields('020')
    record['isbn'] = id_match(isbn_fields, ISBN_RE)
        
    upc_fields = marc_record.get_fields('024')
    record['upc'] = id_match(upc_fields, UPC_RE)

    if marc_record['041']:
        language_dubbed_codes = marc_record['041'].get_subfields('a')
        languages_dubbed = get_languages(language_dubbed_codes)
        record['language_dubbed'] = []
        for language in languages_dubbed:
            if language != record['language']:
                record['language_dubbed'].append(language)
        language_subtitles_codes = marc_record['041'].get_subfields('b')
        languages_subtitles = get_languages(language_subtitles_codes)
        if languages_subtitles:
            record['language_subtitles'] = languages_subtitles
    record['access'] = get_access(marc_record)
    record['author'] = marc_record.author()
    record['callnum'] = get_callnumber(marc_record)
    record['item_ids'] = get_items(marc_record,ils)
    record['lc_firstletter'] = get_lcletter(marc_record)
    record['location'] = get_location(marc_record)
    # are there any subfields we don't want for the full_title?
    if marc_record['245']:
        full_title = marc_record['245'].format_field()
        try:
            nonfiling = int(marc_record['245'].indicator2)
        except ValueError:
            nonfiling = 0
        record['full_title'] = full_title
        title_sort = full_title[nonfiling:].strip()
        # good idea, but need to convert to unicode first
        #title_sort = unicodedata.normalize('NFKD', title_sort)
        record['title_sort'] = title_sort
        if marc_record.title() is not None:
            record['title'] = marc_record['245']['a'].strip(' /:;')
        else:
            record['title'] = full_title
    
    if marc_record['260']:
        record['imprint'] = marc_record['260'].format_field()
        record['publisher_location'] = normalize(marc_record['260']['a'])
        record['publisher'] = normalize(marc_record['260']['b'])
        # grab date from 008
        #if marc_record['260']['c']:
        #    date_find = DATE_RE.search(marc_record['260']['c'])
        #    if date_find:
        #        record['date'] = date_find.group()

    description_fields = marc_record.get_fields('300')
    record['description'] = [field.value() for field in description_fields]
    
    series_fields = marc_record.get_fields('440', '490')
    record['series'] = multi_field_list(series_fields, ['a','v'])

    notes_fields = marc_record.get_fields('500','501','502','503','504','505','506','507',
                                          '509','510','512','513','514','515','516','517',
                                          '518','519','521','545','547','590')
    record['notes'] = [field.value() for field in notes_fields]
    
    contents_fields = marc_record.get_fields('505')
    record['contents'] = multi_field_list(contents_fields, 'a')
    
    summary_fields = marc_record.get_fields('520')
    record['summary'] = [field.value() for field in summary_fields]
       
    subjentity_fields = marc_record.get_fields('610')
    subjectentities = multi_field_list(subjentity_fields, 'ab')
    
    subject_fields = marc_record.subjects()  # gets all 65X fields

    genres = []
    topics = []
    places = []
    for field in subject_fields:
        genres.extend(subfield_list(field, 'v'))
        topics.extend(subfield_list(field, 'x'))
        places.extend(subfield_list(field, 'z'))
        if field.tag == '650':
            if field['a'] != 'Video recordings for the hearing impaired.':
                topics.append(normalize(field['a']))
        elif field.tag == '651':
            places.append(normalize(field['a']))
        elif field.tag == '655':
            if field['a'] != 'Video recordings for the hearing impaired.':
                genres.append(normalize(field['a']))
        #for subfield_indicator in ('a', 'v', 'x', 'y', 'z'):
        #    more_topics = subfield_list(subfield_indicator)
        #    topics.extend(more_topics)
    # Process through Subject name fields and add to topics
    topics.extend(get_subject_names(marc_record))
    record['genre'] = set(genres)
    record['topic'] = set(topics)
    record['place'] = set(places)

    personal_name_fields = marc_record.get_fields('700')
    record['personal_name'] = []
    for field in personal_name_fields:
        subfields = field.get_subfields('a', 'b', 'c', 'd')
        personal_name = ' '.join([x.strip() for x in subfields])
        record['personal_name'].append(personal_name)

    corporate_name_fields = marc_record.get_fields('710')
    record['corporate_name'] = []
    for field in corporate_name_fields:
        subfields = field.get_subfields('a', 'b')
        corporate_name = ' '.join([x.strip() for x in subfields])
        record['corporate_name'].append(corporate_name)

    url_fields = marc_record.get_fields('856')
    record['url'] = []
    for field in url_fields:
        url_subfield = field.get_subfields('u')
        if url_subfield:
            record['url'].append(url_subfield[0])
    record['marc_record'] = marc_record.__str__() # Should output to MARCMaker format
    return record

def get_row(record):
    """Converts record dict to row for CSV input."""
    row = RowDict(record)
    return row

def write_csv(marc_file_handle, csv_file_handle, collections=None, 
        ils=settings.ILS):
    """
    Convert a MARC dump file to a CSV file.
    """
    # This doctest commented out until field names are stable.
    #>>> write_csv('test/marc.dat', 'test/records.csv')
    #>>> csv_records = open('test/records.csv').read()
    #>>> csv_measure = open('test/measure.csv').read()
    #>>> csv_records == csv_measure
    #True
    #>>> os.remove('test/records.csv')

    # TODO: move xml parsing to marcxml parser
    #if in_xml:
    #    reader = pymarc.marcxml.parse_xml_to_array(marc_file_handle)
    #else:
    reader = pymarc.MARCReader(marc_file_handle)
    fieldname_dict = {}
    for fieldname in FIELDNAMES:
        fieldname_dict[fieldname] = fieldname
    #for record in reader
    count = 0
    logging.info("Started MARC record import into Aristotle")
    try:
        writer = csv.DictWriter(csv_file_handle, FIELDNAMES)
        writer.writerow(fieldname_dict)
        for marc_record in reader:
            count += 1
            try:
                record = get_record(marc_record, ils=ils)
                if record:  # skip when get_record returns None
                    if collections:
                        new_collections = []
                        old_record = get_old_record(record['id'])
                        if old_record:
                            old_collections = old_record.get('collection')
                            if old_collections:
                                new_collections.extend(old_collections)
                        new_collections.extend(collections)
                        try:
                            record['collection'].extend(new_collections)
                        except (AttributeError, KeyError):
                            record['collection'] = new_collections
                    row = get_row(record)
                    writer.writerow(row)
            except:
                if marc_record.title() is not None:
                    title = marc_record.title()
                else:
                    title = marc_record['245'].format_field()
                logging.info(u"%s error at count=%s, titles is '%s'" %\
                            (sys.exc_info()[0],
                             count,
                             title))
                sys.stderr.write("\nError in MARC record #%s (%s):\n" % 
                        (count, title.encode('ascii', 'ignore')))
                raise
            else:
                if count % 1000:
                    sys.stderr.write(".")
                else:
                    logging.info("\t%s records processed" % count)
                    sys.stderr.write(str(count))
    finally:
        marc_file_handle.close()
        csv_file_handle.close()
    logging.info("Processed %s records.\n" % count)
    sys.stderr.write("\nProcessed %s records.\n" % count)
    return count

def get_old_record(id):
    id_query = 'id:%s' % id
    params = [
        ('fq', id_query.encode('utf8')),
        ('q.alt', '*:*'),
        ('qt', 'dismax'),
        ('wt', 'json'),
    ]
    urlparams = urllib.urlencode(params)
    url = '%sselect?%s' % (settings.SOLR_URL, urlparams)
    try:
        solr_response = urllib.urlopen(url)
    except IOError:
        raise IOError, 'Unable to connect to the Solr instance.'
    try:
        response = simplejson.load(solr_response)
    except ValueError, e:
        print urllib.urlopen(url).read()
        raise ValueError, 'Solr response was not a valid JSON object.'
    try:
        doc = response['response']['docs'][0]
    except IndexError:
        doc = None
    return doc


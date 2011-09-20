#
# mods.py - MODS Repository Solr Parser 
#
# Copyright 2011 Jeremy Nelson
#

"""Helpers for MARC processing."""

import csv
import re
import sys
import time
import unicodedata
import urllib

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import simplejson

from aristotle.discovery.parser import marc


try:
    set
except NameError:
    from sets import Set as set

# local libs
import mods_maps

ISBN_RE = re.compile(r'(\b\d{10}\b|\b\d{13}\b)')
UPC_RE = re.compile(r'\b\d{12}\b')
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
    'format',
    'full_title',
    'genre',
    'hdl_handle',
    'id',
    'imprint',
    'isbn',
    'language',
    'language_dubbed', 
    'language_subtitles',
    'location',
    'notes',
    'personal_name',
    'pid',
    'place',
    'publisher',
    'pubyear',
    'series',
    'summary',
    'title',
    'title_sort',
    'topic',
    'upc',
    'url',
]


# Helper functions
def get_names(mods_record):
    """Cycles through name list and returns author and
    advisor names."""
    output = {'advisors':[],
              'authors':[]}
    for name in mods_record.names:
        for role in name:
            if role.type == 'advisor':
                output['advisors'].append(name.display_form)
            if role.type == 'author':
                output['author'].append(name.display_form)
    return output
            

def get_titles(mods_record):
    """Extracts the title and a sort title from the modsTitle
    element.
    """
    title = mods_record.title
    title_sort = None
    return (title,title_sort)

def get_record(mods_record):
    """
    Pulls the fields from MODS object into a dictionary.
    """
    record = {}
    record = get_names(mods_record,record)
    record['id'] = mods_record.pid
    record['title'],record['title_sort']  = get_titles(mods_record)
    record['publisher'] = mods_record.originInfo.publisher

    # Dump all fields into text 
    for field in mods_record:
        record['text'] += str(field)
    return record

def get_row(record):
    """Converts record dict to row for CSV input."""
    row = marc.RowDict(record)
    return row

def write_csv(mods_file_handle, csv_file_handle, collections=None, 
        ils=settings.ILS):
    """
    Convert a MODS dump file to a CSV file.
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
    fieldname_dict = {}
    for fieldname in FIELDNAMES:
        fieldname_dict[fieldname] = fieldname
    #for record in reader
    count = 0
    try:
        writer = csv.DictWriter(csv_file_handle, FIELDNAMES)
        writer.writerow(fieldname_dict)
        for mods_record in reader:
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
                sys.stderr.write("\nError in MARC record #%s (%s):\n" % 
                        (count, title.encode('ascii', 'ignore')))
                raise
            else:
                if count % 1000:
                    sys.stderr.write(".")
                else:
                    sys.stderr.write(str(count))
    finally:
        mods_file_handle.close()
        csv_file_handle.close()
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


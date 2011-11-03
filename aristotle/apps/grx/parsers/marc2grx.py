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

logging.basicConfig(filename='%slog/%s-grx-solr-indexer.log' % (settings.BASE_DIR,
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

from apps.discovery.parsers.marc import RowDict,normalize,subfield_list,multi_field_list,id_match,get_languages,get_row,write_csv

NONINT_RE = re.compile(r'\D')
FIELDNAMES = [
    'id',
    'grx_title',
    'language',
    'subtitles',
    'summary',
    'title',
    'url',
]

        
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

    try:
        if ils == 'Horizon':
            record['id'] = marc_record['999']['a']
        elif ils == 'III':
            # [1:-1] because that's how it's referred to in the opac
            record['id'] = marc_record['907']['a'][1:-1]
        elif ils == 'Unicorn':
            record['id'] = marc_record['35']['a']
        else:
            record['id'] = marc_record['001'].value()
    except AttributeError:
        return
    
    # First checks for a varing form of the title to set grx_title,
    # otherwise set to the same value as general title
    if marc_record['246'] is not None:
        grx_titles = marc_record.get_fields('246')
        if len(grx_titles) > 0:
            subfields = grx_titles[0].get_subfields('a','i')
            grx_normalized_title = ''
            for field in subfields:
                grx_normalized_title += normalize(field)
            if grx_normalized_title.startswith('Colorado College:'):
                grx_normalized_title = grx_normalized_title.replace('Colorado College:ia','')
            record['grx_title'] = grx_normalized_title
    if marc_record['245']:
        full_title = marc_record['245'].format_field()
        try:
            nonfiling = int(marc_record['245'].indicator2)
        except ValueError:
            nonfiling = 0
        record['title'] = full_title
        if not record.has_key('grx_title'):
            record['grx_title'] = full_title
    if marc_record['590']:
        record['summary'] = normalize(marc_record['590']['a'])
    url_fields = marc_record.get_fields('856')
    record['url'] = []
    for field in url_fields:
        url_subfield = field.get_subfields('u')
        if url_subfield:
            record['url'].append(url_subfield[0])
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
    logging.info("Started MARC record import into GRX core")
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

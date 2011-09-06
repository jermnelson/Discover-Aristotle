# Copyright 2008 Gabriel Sean Farrell
# Copyright 2008 Mark A. Matienzo
#
# This file is part of Kochief.
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

"""Imports CSV data into a Solr instance."""

import os
import urllib

SOLR_URL = 'http://localhost:8983/solr/update/csv?%s'

MULTIVALUE_FIELDNAMES = [
    'contents',
    'corporate_name',
    'genre',
    'isbn',
    'language_dubbed',
    'language',
    'language_subtitles',
    'notes',
    'personal_name',
    'place',
    'position',
    'series',
    'summary',
    'topic',
    'url',
]

# summary causes an error in solr pre 2008/01/08 dev (for my data, at
# least -- gsf) -- see 
# http://mail-archives.apache.org/mod_mbox/lucene-solr-user/200801.mbox/%3cc68e39170801081009r18b024f9g4076a6333455463e@mail.gmail.com%3e

def load_solr(csv_file, solr_url):
    """
    Load CSV file into Solr.  solr_params are a dictionary of parameters
    sent to solr on the index request.
    """
    file_path = os.path.abspath(csv_file)
    solr_params = {}
    for fieldname in MULTIVALUE_FIELDNAMES:
        tag_split = "f.%s.split" % fieldname
        solr_params[tag_split] = 'true'
        tag_separator = "f.%s.separator" % fieldname
        solr_params[tag_separator] = '|'
    solr_params['stream.file'] = file_path
    solr_params['commit'] = 'true'
    params = urllib.urlencode(solr_params)
    print "Loading records into Solr ..."
    try: 
        output = urllib.urlopen(solr_url % params)
    except IOError:
        raise IOError, 'Unable to connect to the Solr instance.'
    print "Solr response:\n"
    print output.read()


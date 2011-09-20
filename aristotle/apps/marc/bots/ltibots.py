"""
  ltibots.py -- LTI Sort Bots
"""
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright: 2011 Colorado College
from pymarc import MARCReader

class LTISortBot(object):
    """
    Class reads an LTI load file and sorts all fields by number
    with no other validation.
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

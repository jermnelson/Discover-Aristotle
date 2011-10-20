"""
 forms.py - Forms for uploading and downloading MARC records
"""
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
__author__ = 'Jeremy Nelson, Cindy Tappan'

import logging,re
from django import forms
from models import Notes,RecordLoadLog

class MARCRecordUploadForm(forms.Form):
    """This form contains fields that are necessary for MARC record loads"""
    raw_marc_record = forms.FileField(required=True,label="Single MARC File")
    record_type = forms.ChoiceField(required=True,
                                    label="Record Type",
                                    choices= [(1,"Bibliographic"),
                                              (2,"Name Authority"),
                                              (3,"Subject Authority")])
    load_table = forms.ChoiceField(required=True,
                                    label="Load Table",
                                    choices= [(1,"blackdrama"),
                                              (2,"LTI bibs")])
    notes = forms.CharField(required=False,label="Notes")  

class NotesForm(forms.ModelForm):
    """`NotesForm` is a Django form model for the `Notes` model
    """
         
    class Meta:
        model = Notes
        widgets = {
            'note_value':forms.Textarea(attrs={'cols':35,'rows':4}),
        }
            
class RecordLoadLogForm(forms.ModelForm):
    """`RecordLoadLogForm` is a django model form for adding a new
    RecordLoadLog after running the bot on the original MARC record
    uploaded file"""

    class Meta:
        model = RecordLoadLog
        #fields = ('original_file','record_type','load_table','source_id')
        widgets = {
            'load_table':forms.Select(choices=[(1,"blackdrama"),
                                               (2,"LTI bibs")]),
            'record_type':forms.Select(choices=[(1,"Bibliographic"),
                                                (2,"Name Authority"),
                                                (3,"Subject Authority")])}

class UpdateRecordLoadLogForm(forms.ModelForm):
    """`UpdateRecordLoadLogForm` is a Django model form for updating 
    an `RecordLoadLog`.
    """

    class Meta:
        model = RecordLoadLog
        fields = ('new_records',
                  'overlaid_records',
                  'rejected_records',
                  'ils_result')

# forms.py --- Custom Forms for Dataset ingestion and management for Fedora
# sever.
#
# 2011 (c) Colorado College
#
__author__ = 'Jeremy Nelson'
import logging
from django import forms
from eulxml.xmlmap import mods
from eulxml.forms import XmlObjectForm,SubformField

class ThesisDatasetForm(forms.Form):
    """DatasetForm associates a form with multiple MODS elements to support a
    thesis dataset in the Fedora object
    """

    abstract = forms.CharField(required=False,
                               label='Abstract of dataset',
                               widget=forms.Textarea(attrs={'cols':60,
                                                            'rows':5}))
    is_publically_available = forms.BooleanField(required=False,label='I agree')
    info_note = forms.CharField(required=False,
                                label='Software/version',
                                widget=forms.Textarea(attrs={'cols':60,
                                                             'rows':5}))
    dataset_file = forms.FileField(required=False,
                                   label='Dataset')

    def is_empty(self):
        for k,v in self.cleaned_data.iteritems():
            if v != None:
                return False
        return True


    def mods(self,
             mods_xml=None):
        """
        Method supports adding a dataset file stream and associated MODS elements,
        creates a new MODS XML datastream if not present.
        """
        if not mods_xml:
            mods_xml = mods.MODS()
        if self.cleaned_data.has_key('abstract'):
            abstract = mods.Note(text=self.cleaned_data['abstract'],
                                # type='source type',
                                 label='Dataset Abstract')
            mods_xml.notes.append(abstract)
        if self.cleaned_data.has_key('info_note'):
            info = mods.Note(text=self.cleaned_data['info_note'],
                             #type='source note',
                             label='Dataset Information')
            mods_xml.notes.append(info)
        return mods_xml


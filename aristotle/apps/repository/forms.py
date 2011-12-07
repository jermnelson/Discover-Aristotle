"""
 :mod:`repository.forms` Django forms for Aristotle's Repository Utilities
"""
__author__ = "Jeremy Nelson"

from django import forms
from models import ADRBasicContentModel
from eulfedora.server import Repository

class MoverForm(forms.Form):
    """
    `MoverForm` allows a user to input a Fedora Commons Repository PID and
    a new parent collection PID for moving the object.
    """
    collection_pid = forms.CharField(max_length=20,
                                     label="PID of target collection",
                                     help_text='PID of target collection')

    source_pid = forms.CharField(max_length=20,
                                 label="PID of source PID",
                                 help_text='PID of source Fedora Object')

    def clean(self):
        repository = Repository()
        mover_data = self.cleaned_data
        collection_pid = mover_data.get('collection_pid')
        source_pid = mover_data.get('source_pid')

        if collection_pid and source_pid:
            if not repository.find_objects(pid=collection_pid):
                raise forms.ValidationError("Collection PID %s not found in repository" % collection_pid)
            if not repository.find_objects(pid=source_pid):
                raise forms.ValidationError("Source PID %s not found in repository" % source_pid)
 
        return self.cleaned_data


          
        

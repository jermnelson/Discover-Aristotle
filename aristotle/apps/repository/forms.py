"""
 :mod:`repository.forms` Django forms for Aristotle's Repository Utilities
"""
__author__ = "Jeremy Nelson"

import logging
from django import forms
from eulfedora.server import Repository
from eulfedora.util import RequestFailed

repository = Repository()

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

    def clean_collection_pid(self):
        """
        Custom clean method for :class:`MoverForm.collection_pid` checks to see
        if PID exists in Repository, raise :mod:`forms.ValidationError` if PID
        not present.
        """
        data = self.cleaned_data['collection_pid']
        if data is not None:
            try:
                collection_object = repository.api.getObjectHistory(pid=data)
            except RequestFailed:
                raise forms.ValidationError("Collection PID %s not found in repository" % data)
        return data


    def clean_source_pid(self):
        """
        Custom clean method for :class:`MoverForm.collection_pid` checks to see
        if PID exists in Repository, raise :mod:`forms.ValidationError` if PID
        not present.
        """
        data = self.cleaned_data['source_pid']
        if data is not None:
            try:
                source_object = repository.api.getObjectHistory(pid=data)
            except RequestFailed:
                raise forms.ValidationError("Source PID %s not found in repository" % data)
        return data

from django import forms

class BasicSearchForm(forms.Form):
    """
    Basic search form provides a single text field and a drop-down list
    """
    search_phrase = forms.CharField(required=False)
    

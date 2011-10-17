"""
  views.py - Views for III systems utilities
"""
__author__ = 'Jeremy Nelson'


from django.views.generic.simple import direct_to_template
from vendors.iii.models import FundRecord,FundReportLog

def index(request):
    """
    Displays list of utilities for III
    """
    return direct_to_template(request,
                              'vendors/iii/index.html'
                              {'utilities':[]})


def banner(request):
    """
    Displays a simple form with a file-upload field. If POST,
    takes a CSV of order records, search and replace each occurrence
    of Fund code with full fund value before returning a page to 
    download modified CSV file.
    """
    if request.method == 'POST':
        pass # Should take and open file 
    

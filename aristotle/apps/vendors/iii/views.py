"""
  views.py - Views for III systems utilities
"""

__author__ = 'Jeremy Nelson'

import csv,datetime
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from vendors.iii.models import Fund,FundProcessLog
from vendors.iii.forms import CSVUploadForm
from vendors.iii.bots.iiibots import FundBot

def csv(request):
    """
    Displays a simple form with a file-upload field. If POST,
    takes a CSV of order records, search and replace each occurrence
    of Fund code with full fund value before returning a page to 
    download modified CSV file.
    """
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            fund_bot = FundBot(csv_file=request.FILES['csv_file'])
            filename = '%s-banner-iii.csv' % datetime.datetime.today().strftime('%Y-%m-%d')
            response = HttpResponse(mimetype="text/csv")
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
   
            csv_response = fund_bot.process(response)
            new_log = FundProcessLog(substitutions=int(fund_bot.substitutions))
            new_log.save()
            return csv_response
    else:
        return direct_to_template(request,
                                  'vendors/iii/csv.html',
                                 {'form':CSVUploadForm()})



def index(request):
    """
    Displays list of utilities for III
    """
    fund_logs = FundProcessLog.objects.all()
    activity_logs = []
    for log in fund_logs:
       activity_logs.append({'activity_date':log.created_on,
                             'description': '%s fund codes subsituted' % log.substitutions})
    utilities = [{'name':'csv',
                  'label':'Expand Fund codes to values',
                  'description':'''Takes order records in CSV format, replaces Fund codes with
                                   expanded Fund numeric values'''}]
    return direct_to_template(request,
                              'vendors/iii/index.html',
                              {'activity_log':activity_logs,
                               'utilities':utilities})


    

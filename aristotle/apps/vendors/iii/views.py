"""
  views.py - Views for III systems utilities
"""

__author__ = 'Jeremy Nelson'

import csv,datetime,logging
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login

from django.views.generic.simple import direct_to_template
from vendors.iii.models import Fund,FundProcessLog
from vendors.iii.forms import CSVUploadForm,PatronLoginForm
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

def patron_login(request):
    """
    Processes login request posted from form, if redirect url exists,
    redirect's user.
    """
    if request.method == 'POST':
        redirect_url = None
        if request.POST.has_key('redirect'):
            redirect_url = request.POST['redirect']
        last_name = request.POST['last_name']
        iii_patron_id = request.POST['iii_patron_id']
        user = authenticate(last_name=last_name,iii_id=iii_patron_id)
        if user is not None:
            login(request,user)
            if redirect_url is not None:
                return HttpResponseRedirect(redirect_url)
            else:
                return direct_to_template(request,
                                         'vendors/iii/login.html',
                                        {'form':None})
        else:
            direct_to_template(request,
                                  'vendors/iii/login.html',
                                  {'form':PatronLoginForm(),
                                   'msg':'Invalid login, please try again'})
    else:
        return direct_to_template(request,
                                  'vendors/iii/login.html',
                                  {'form':PatronLoginForm(),
                                   'msg':'Please login with TIGER number'})
   

def index(request):
    """
    Displays list of utilities for III
    """
    fund_logs = FundProcessLog.objects.all()
    activity_logs = []
    for log in fund_logs:
       activity_logs.append({'activity_date':log.created_on,
                             'description': '%s fund codes subsituted' % log.substitutions})
    logging.error("Number of activity logs:%s" % len(activity_logs))
    utilities = [{'name':'csv',
                  'label':'Expand Fund codes to values',
                  'description':'''Takes order records in CSV format, replaces Fund codes with
                                   expanded Fund numeric values'''}]
    return direct_to_template(request,
                              'vendors/iii/index.html',
                              {'activity_log':activity_logs,
                               'utilities':utilities})


    

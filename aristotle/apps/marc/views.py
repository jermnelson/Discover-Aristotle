"""
  views.py -- Views for MARC record manipulation
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
#
__author__ = 'Jeremy Nelson, Cindy Tappan'

import logging,zlib,datetime,os

from django import forms
from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.servers.basehttp import FileWrapper
from django.template import RequestContext
from forms import MARCRecordUploadForm,RecordLoadLogForm,NotesForm,UpdateRecordLoadLogForm
from models import RecordLoadLog

# Imports Bots
from bots.aspbots import AlexanderStreetPressMusicBot,BlackDramaBot
from bots.aspbots import WomenSocialMovementsBot,GarlandEWMOBot
from bots.awbots import AmericanWestBot
from bots.eccobots import ECCOBot
from bots.galebots import GVRLBot
from bots.gutenbergbots import ProjectGutenbergBot
from bots.opbots import OxfordHandbooksOnlineBot,OxfordReferenceOnlineBot
from bots.springerbots import SpringerEBookBot
from bots.video_bots import FilmsOnDemand

active_bots = [AlexanderStreetPressMusicBot,
               AmericanWestBot,
               BlackDramaBot,
               ECCOBot,
               GarlandEWMOBot,
               GVRLBot,
               FilmsOnDemand,
               OxfordHandbooksOnlineBot,
               OxfordReferenceOnlineBot,
               ProjectGutenbergBot,
               SpringerEBookBot,
               WomenSocialMovementsBot]

def default(request):
    """Default view for MARC utilities Django application
    """
    history = RecordLoadLog.objects.all()
    return direct_to_template(request,
                              'marc/index.html',
                              {'active_bots':active_bots,
                               'history':history})

def download(request):
    """Download modified MARC21 file"""
    log_pk = request.session['log_pk']
    record_log = RecordLoadLog.objects.get(pk=log_pk)
    modified_file = open(record_log.modified_file.path,'r')
    file_wrapper = FileWrapper(file(record_log.modified_file.path))
    response = HttpResponse(file_wrapper,content_type='text/plain')
    filename = os.path.split(record_log.modified_file.path)[1]
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['Content-Length'] = os.path.getsize(record_log.modified_file.path)
    return response

def process(request):
    """Takes form submission and runs bots on uploaded 
    form."""
    if request.method != 'POST':
        raise Http404
    else:
        record_log_form = RecordLoadLogForm(request.POST,request.FILES)
    bot_name,bot = request.POST['bot'],None
    for active_bot in active_bots:
        if active_bot.__name__ == bot_name:
            if request.POST.has_key('databases'):
                bot = active_bot(marc_file=request.FILES['original_file'],
                                 type_of=request.POST['databases'])
            else:
                bot = active_bot(marc_file=request.FILES['original_file'])
    if not bot:
        raise Http404
    bot.load()
    if not record_log_form.is_valid():
        logging.error("Errors = %s" % record_log_form.errors)
    record_log = record_log_form.save()
    record_log.process_id = bot_name
    record_log.save()
    
    mod_filename = '%s-%s.mrc' % (datetime.datetime.today().strftime("%Y-%m-%d"),
                                  record_log.process_id.replace('Bot',''))
    #record_log.modified_file_content = File(mod_filename)
    #record_log.modified_file_content.write(bot.to_text())
    record_log.modified_file.save(mod_filename,ContentFile(bot.to_text()))
    request.session['log_pk'] = record_log.pk
    note_form = NotesForm(request.POST)
    note_form.record_load_log_id = record_log.pk
    if note_form.is_valid():
        note_form.save()
    else:
        logging.error("Note form is not valid %s" % note_form.errors)
    return HttpResponseRedirect("/marc/update")
    #return HttpResponse('IN MARC BOT process %s' % record_log.pk)

def record_load(request,bot_name):
    """Record load view displays the `MARCRecordUploadForm` for a
    particular MARC record load.

    :param bot_name: Name of bot, required"""
    bot_names = [bot.__name__ for bot in active_bots]
    is_active = bot_names.count(bot_name)
    if is_active < 1:
        raise Http404
    marc_form = RecordLoadLogForm()
    note_form = NotesForm()
    for bot in active_bots:
        if bot.__name__ == bot_name and hasattr(bot,'DATABASES'):
            bot_choices = []
            for k,v in getattr(bot,'DATABASES').iteritems():
                bot_choices.append((v['code'],k))
            marc_form.fields['databases']=forms.ChoiceField(label='Select database',
                                                            required=False,
                                                            choices=bot_choices)
           
    return direct_to_template(request,
                              'marc/index.html',
                              {'active_bots':active_bots,
                               'live_bot':bot_name,
                               'download':None,
                               'marc_form':marc_form,
                               'note_form':note_form})

def search(request):
   """Search takes a query string and searches the 
   RecordLoadLog and docstrings of Bot classes.
   """
   return HttpResponse("IN MARC search")

def update_log(request):
    """Displays download link and update log form after
    successful bot processing."""
    log_pk = request.session['log_pk']
    marc_form = UpdateRecordLoadLogForm()
    note_form = NotesForm()
    download = True
    return direct_to_template(request,
                              'marc/index.html',
                              {'active_bots':active_bots,
                               'live_bot':None,
                               'download':download,
                               'marc_form':marc_form,
                               'note_form':note_form})


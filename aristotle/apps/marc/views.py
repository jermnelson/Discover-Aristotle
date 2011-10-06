"""
  views.py -- Views for MARC record manipulation
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

import logging

from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect,HttpResponse
from django.template import RequestContext
from forms import MARCRecordUploadForm

# Imports Bots
from bots.aspbots import AlexanderStreetPressMusicBot,BlackDramaBot
from bots.aspbots import WomenSocialMovementsBot,GarlandEWMOBot
from bots.awbots import AmericanWestBot
from bots.eccobots import ECCOBot
from bots.galebots import GVRLBot
from bots.gutenbergbots import ProjectGutenbergBot
from bots.opbots import OxfordHandbooksOnlineBot,OxfordReferenceOnlineBot
from bots.springerbots import SpringerEBookBot

active_bots = [AlexanderStreetPressMusicBot,
               AmericanWestBot,
               BlackDramaBot,
               ECCOBot,
               GarlandEWMOBot,
               GVRLBot,
               OxfordHandbooksOnlineBot,
               OxfordReferenceOnlineBot,
               ProjectGutenbergBot,
               SpringerEBookBot,
               WomenSocialMovementsBot]

def default(request):
    """Default view for MARC utilities Django application
    """
    return direct_to_template(request,
                              'marc/index.html',
                              {'active_bots':active_bots})

def process(request):
    """Takes form submission and runs bots on uploaded 
    form."""
    if request.method != 'POST':
        raise Http404
    return HttpResponse('IN MARC BOT process')

def record_load(request,bot_name):
    """Record load view displays the `MARCRecordUploadForm` for a
    particular MARC record load."""
    bot_names = [bot.__name__ for bot in active_bots]
    is_active = bot_names.count(bot_name)
    if is_active < 1:
        raise Http404
    marc_form = MARCRecordUploadForm()
    return direct_to_template(request,
                              'marc/index.html',
                              {'active_bots':active_bots,
                               'live_bot':bot_name,
                               'marc_form':marc_form})

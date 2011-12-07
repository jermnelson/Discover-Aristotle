"""
 :mod:`apps.repository.views` - Views for Aristotle Repository Utilities
"""
__author__ = "Jeremy Nelson"

import settings
from forms import MoverForm
from eulfedora.server import Repository
from django.views.generic.simple import direct_to_template

def default(request):
    """
    Displays default view for Repository Templates

    :param request: Django request
    """
    return direct_to_template(request,
                              'repository/index.html',
                              {})

def object_mover(request):
    """
    Displays and process form for moving objects by their PID to
    a different parent PID

    :param request: Django request
    """
    if request.method == 'POST':
        repository = Repository()
        mover_form = MoverForm(request.POST)
        if mover_form.is_valid():
            collection_pid = mover_form.cleaned_data['collection_pid']
            source_pid = mover_form.cleaned_data['source_pid']
            message = 'PID %s moved to collection PID %s' % (source_pid,
                                                             collection_pid)
            return direct_to_template(request,
                                      'repository/index.html',
                                      {'message':message})
    else:
        mover_form = MoverForm()
    return direct_to_template(request,
                              'repository/index.html',
                              {'mover_form':mover_form})
 

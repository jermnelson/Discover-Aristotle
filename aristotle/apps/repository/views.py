"""
 :mod:`apps.repository.views` - Views for Aristotle Repository Utilities
"""
__author__ = "Jeremy Nelson"

import settings,logging
from lxml import etree
from forms import MoverForm
from models import RepositoryMovementLog
from eulfedora.server import Repository
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template


def default(request):
    """
    Displays default view for Repository Templates

    :param request: Django request
    """
    logs = RepositoryMovementLog.objects.all()
    return direct_to_template(request,
                              'repository/index.html',
                              {'history':logs})

def object_mover(request):
    """
    Displays and process form for moving objects by their PID to
    a different parent PID

    :param request: Django request
    """
    if request.method == 'POST':
        mover_form = MoverForm(request.POST)
        if mover_form.is_valid():
            collection_pid = mover_form.cleaned_data['collection_pid']
            source_pid = mover_form.cleaned_data['source_pid']
            repository_move(source_pid,collection_pid)
            new_log = RepositoryMovementLog(collection_pid=collection_pid,
                                            source_pid=source_pid)
            new_log.save()
            message = 'PID %s moved to collection PID %s' % (source_pid,
                                                             collection_pid)
            return direct_to_template(request,
                                      'repository/index.html',
                                      {'history': RepositoryMovementLog.objects.all(),
                                       'message':message})
    else:
        mover_form = MoverForm()
    return direct_to_template(request,
                              'repository/index.html',
                              {'history':RepositoryMovementLog.objects.all(),
                               'mover_form':mover_form})

def repository_move(source_pid,collection_pid):
    """
    Helper view function takes a source_pid and collection_pid, 
    retrives source_pid RELS-EXT and updates 
    fedora:isMemberOfCollection value with new collection_pid

    :param source_pid: Source Fedora Object PID
    :param collection_pid: Collection Fedora Object PID
    """
    ns = {'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
          'fedora':'info:fedora/fedora-system:def/relations-external#'}

    repository = Repository()
    raw_rels_ext = repository.api.getDatastreamDissemination(pid=source_pid,
                                                             dsID='RELS-EXT')
    rels_ext = etree.XML(raw_rels_ext[0])
    collection_of = rels_ext.find('{%s}Description/{%s}isMemberOfCollection' %\
                                  (ns['rdf'],ns['fedora']))
    if collection_of is not None:
        collection_of.attrib['{%s}resource' % ns['rdf']] = "info:fedora/%s" % collection_pid
    logging.error("RELS-EXT XML=%s" % rels_ext)
    repository.api.modifyDatastream(pid=source_pid,
                                    dsID="RELS-EXT",
                                    dsLabel="RELS-EXT",
                                    mimeType="application/rdf+xml",
                                    content=etree.tostring(rels_ext))


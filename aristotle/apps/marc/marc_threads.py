"""
 marc_threads.py -- Thread classes for indexing MARC files into various Solr
 cores.
"""

__author__ = 'Jeremy Nelson'
import sys,datetime
import Queue,threading,logging
import solr,pymarc
import aristotle.settings as settings

from django.conf import settings

marc_records_queue = Queue.Queue()

logging.basicConfig(filename='%slog/%s-marc-multithread-thread.log' % (settings.BASE_DIR,
                                                                       datetime.datetime.today().strftime('%Y%m%d-%H')),
                    level=logging.INFO)

class MARCIndexThread(threading.Thread):
    """
    `MARCIndexThread` class runs a specified MARC parser on a set of MARC
    records to index into a Solr server.
    """

    def run(self):
        """
        Method runs `MARCIndexThread` in a thread, waits for a message
        containing a list of MARC records along with an URL to the Solr
        server and core.
        """
        message =  marc_records_queue.get()
        sys.stderr.write("\tIn thread %s\n" % message.get('name'))
        marc_records = message.get('records')
        parser = message.get('parser')
        solr_url = message.get('solr_url')
        sys.stderr.write("Before solr instance url=%s" % solr_url)
        solr_server = solr.Solr(solr_url)
        sys.stderr.write("After solr instance")
        for i,raw_record in enumerate(marc_records):
            record = pymarc.Record(data=raw_record)
            solr_document = parser.get_record(record,settings.ILS)
            solr_server.add(solr_document, commit=True)
        sys.stderr.write("\tThread %s finished adding %s documents to Solr" % (message.get('name'),
                                                                               len(marc_record)))
  #      except Exception, e:
  #          error_msg = "Unable to index MARC record load Exception: %s" % str(e)
  #          sys.stderr.write(error_msg)
  #          logging.error(error_msg)
        marc_records_queue.task_done()

def start_indexing():
    """
    `start_indexing` function creates and starts a `MARCIndexThread` worker
    thread.
    """
    worker = MARCIndexThread()
    worker.start()
    sys.stderr.write("Starting Indexer thread")     

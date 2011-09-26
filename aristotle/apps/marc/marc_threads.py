"""
 marc_threads.py -- Thread classes for indexing MARC files into various Solr
 cores.
"""

__author__ = 'Jeremy Nelson'

import Queue,threading,logging
import sunburnt
import aristotle.settings as settings

marc_records_queue = Queue.Queue()

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
        try:
            marc_records = message.get('records')
            parser = message.get('parser')
            solr_url = message.get('solr_url')
            solr = sunburnt.SolrInterface(solr_url)
            for record in marc_records:
                solr_document = parser.get_record(record,settings.ILS)
                solr.add(solr_document)
        except Exception, e:
            logging.error("Unable to index MARC record load Exception: %s" % str(e))
        marc_records_queue.task_done()

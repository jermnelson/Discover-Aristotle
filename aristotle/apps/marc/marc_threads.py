"""
 marc_threads.py -- Thread classes for indexing MARC files into various Solr
 cores.
"""

__author__ = 'Jeremy Nelson'
import sys,datetime
import Queue,threading,logging
import csv,pymarc,sunburnt
from aristotle.apps.discovery.parsers import marc
from aristotle.apps.discovery.management.commands import index
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
        marc_records = message.get('records')
        start_msg = "\tIn thread %s total records to be processed are %s\n" % (message.get('name'),
                                                                               len(marc_records))
        sys.stderr.write(start_msg)
        logging.error(start_msg)
        parser = message.get('parser')
        solr_url = message.get('solr_url')
        #solr_server = sunburnt.SolrInterface(solr_url)
        active_records = 0
        start_time = '\tStart processing at %s' %  datetime.datetime.today().ctime()
        sys.stderr.write(start_time)
        logging.error(start_time)
        csv_file_name = '%s.csv' % message.get('name')
        csv_file_handle = open(csv_file_name,'w')
        csv_writer = csv.DictWriter(csv_file_handle, marc.FIELDNAMES)
        field_names = dict()
        for name in marc.FIELDNAMES:
            field_names[name] = name
        csv_writer.writerow(field_names)
        try:
            i = 0
	    for raw_record in marc_records:
	        if raw_record:
		    record = pymarc.Record(data=raw_record)
	            solr_document = parser.get_record(record,settings.ILS)
                    csv_row = marc.get_row(solr_document)
                    csv_writer.writerow(csv_row)
                    #if solr_document:
		    #    for k,v in solr_document.iteritems():
		    #        if not v:
	            #		        k = v
		    #	    elif type(v) == list or type(v) == set:
		    #	        k = [row.encode('ascii','replace') for row in v]
		    #	    elif type(v) == str:
		    #            k = v.encode('ascii','replace')
                    #    try:
		    #        solr_server.add(solr_document)
                    #        solr_server.commit()
                    #        active_records += 1
                    #    except Exception, e:
                    #        error_msg = "Unable to index MARC record id=%s load Exception: %s" % (solr_document['id'],str(e))
                    #        sys.stderr.write(error_msg)
                    #        logging.error(error_msg)
                if not i%1000:
                    location_msg = "\t\t%s:%s.\n" % (message.get('name'),i)
                    sys.stderr.write(location_msg)
                    logging.error(location_msg)
                i += 1
            end_msg = "\tThread %s finished adding %s documents to Solr at %s\n" % (message.get('name'),
                                                                                    active_records,
                                                                                    datetime.datetime.today().ctime())

            sys.stderr.write(end_msg)
            logging.error(end_msg)
            csv_file_handle.close()
        except Exception, e:
            error_msg = "Unable to index MARC record load Exception: %s" % str(e)
            sys.stderr.write(error_msg)
            logging.error(error_msg)
            csv_file_handle.close()
        # Try to call CSV loader
        index.load_solr(csv_file_name)
        marc_records_queue.task_done()

def start_indexing():
    """
    `start_indexing` function creates and starts a `MARCIndexThread` worker
    thread.
    """
    worker = MARCIndexThread()
    worker.start()
    sys.stderr.write("Starting Indexer thread")     

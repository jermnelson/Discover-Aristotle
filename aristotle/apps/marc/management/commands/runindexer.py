"""
  runindexer.py - Runs a multi-threaded MARC record-to-Solr process that 
  shards a large MARC record file into discrete chunks that are then processed
  into one or more Solr cores.
"""

__author__ = 'Jeremy Nelson'
import datetime
import optparse,os,sys
import unicodedata,pymarc
import django.conf as conf
from django.core.management.base import BaseCommand
import settings

from aristotle.apps.marc.marc_threads import marc_records_queue,start_indexing
from aristotle.apps.discovery.parsers import marc as marc_parser

#solr_urls = {'marc_catalog':'http://172.25.1.106:8964/solr/marc_catalog'}
solr_urls = {'marc_catalog':'http://0.0.0.0:8984/solr/marc_catalog'}
parsers = {'marc_catalog':marc_parser}

class Command(BaseCommand):
    """Creates the `runindexer` command for use with Django manage.py
    """
    option_list = BaseCommand.option_list + (
        optparse.make_option('-c','--cores',
            action='store',
            dest='cores',
            metavar='CORES',
            help='Specifies Solr cores that are targeted by indexer,  i.e., --cores=marc_catalog --cores=grx. Default is "marc_catalog"',),
        optparse.make_option('-s','--shard_size',
            action='store',
            dest='shard_size',
            metavar='SHARD_SIZE',
            help='Specifies size of MARC record shard, default is 100k'),
        )
    help = 'Runs multi-threaded indexer for bibliographic records into a Solr server'
    args = '[marc_file...]'

    def handle(self,marc_file,**options):
        """
        Method takes an optional list of cores along with a MARC file or URL 
        and optional listing of cores.
        """
        start_indexing()
        print("Running multi-threaded runindexer on %s file" % marc_file)
        cores = options.get('cores')
        if not cores:
            cores = ['marc_catalog']
        shard_size = options.get('shard_size')
        if not shard_size:
            shard_size = 100000
        else:
            shard_size = int(shard_size)
        marc_records = []
        start_time = datetime.datetime.today()
        print("Loading marc records at %s" % start_time.ctime())
        marc_reader = QuickMARCReader(open(marc_file,'r'))
        total_records = 0
        for i,row in enumerate(marc_reader):
            marc_records.append(row)
            if not (i%shard_size):
                if i != 0:
                    for core in cores:
                        name = "%s - Shard Record span end=%s" % (core,i)
                        print("Creating worker thread for %s" % name)
                        marc_records_queue.put({'records':marc_records,
                                                'solr_url':solr_urls[core],
                                                'parser':parsers[core],
                                                'name':name })
                    marc_records = []
            total_records += 1
            #if i == shard_size +1:
            #    print("Running single shard")
        end_time = datetime.datetime.today()
        print("Finished loading %s records at %s" % (total_records,end_time.ctime()))
        

class QuickMARCReader(object):
     """A quick iterable class for MARC files, breaks MARC21 formatted
     files into record "chunks".
     """

     def __init__(self,marc_file):
         self.file_handle = marc_file


     def __iter__(self):
         return self

     def next(self):
         first5 = self.file_handle.read(5)
         if not first5:
             raise StopIteration
         chunk = self.file_handle.read(int(first5) - 5)
         raw_record = first5 + chunk
         #return raw_record
         #return pymarc.marc8.marc8_to_unicode(raw_record).encode('utf8')
         #return raw_record.decode('utf8','replace')
         #return unicodedata.normalize('NFC',raw_record.decode('utf8','xmlcharrefreplace'))
         return unicode(raw_record,errors='replace')        

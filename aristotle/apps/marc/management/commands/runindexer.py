"""
  runindexer.py - Runs a multi-threaded MARC record-to-Solr process that 
  shards a large MARC record file into discrete chunks that are then processed
  into one or more Solr cores.
"""

__author__ = 'Jeremy Nelson'

import optparse,os,sys
import pymarc
import django.conf as conf
from django.core.management.base import BaseCommand
import settings

from aristotle.apps.marc.marc_threads import marc_records_queue,start_indexing
from aristotle.apps.discovery.parsers import marc as marc_parser

#solr_urls = {'marc_catalog':'http://172.25.1.106:8964/solr/marc_catalog'}
solr_urls = {'marc_catalog':'http://0.0.0.0:8964/solr/marc_catalog'}
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
        # Creates shards 
        marc_records = []
        print("Loading")
        marc_reader = QuickMARCReader(open(marc_file,'r'))
        for row in enumerate(marc_reader):
            marc_records.append(row)
        total_records = len(marc_records)
        total_shards = total_records / shard_size
        if not total_shards:
            total_shards = 1
        print("Shard size=%s, Total records=%s, Total Threads=%s" % (shard_size,
                                                                     total_records,
                                                                     total_shards))
        for shard in range(0,total_shards):
            for core in cores:
                print("\tAdding thread for Shard %s core %s" % (shard,core))
                marc_records_queue.put({'records':marc_records[(shard*shard_size):(shard*shard_size + shard_size)],
                                        'solr_url':solr_urls[core],
                                        'parser':parsers[core],
                                        'name':'Thread %s %s' % (shard,core) })
                    

        

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
         return first5 + chunk
         
                  

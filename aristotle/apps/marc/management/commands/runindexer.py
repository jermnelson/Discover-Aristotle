"""
  runindexer.py - Runs a multi-threaded MARC record-to-Solr process that 
  shards a large MARC record file into discrete chunks that are then processed
  into one or more Solr cores.
"""

__author__ = 'Jeremy Nelson'

import optparse,os,sys
import pymarc
import django.conf as conf
import django.core.management.base as mb
import settings

from aristotle.apps.marc.marc_threads import marc_records_queue
from aristotle.apps.discovery.parsers import marc as marc_parser

solr_urls = {'marc_catalog':settings.SOLR_URL}

class Command(mb.BaseCommand):
    """Creates the `runindexer` command for use with Django manage.py
    """
    option_list = mb.BaseCommand.option_list + (
        optparse.make_option('-c','--cores',
            action='cores',
            dest='cores',
            metavar='CORES',
            help='Specifies Solr cores that are targeted by indexer,  i.e., --cores=marc_catalog --cores=grx. Default is "marc_catalog"',),
        optparse.make_option('-s','--shard_size',
            action='shard_size',
            dest='shard_size',
            metavar='SHARD_SIZE',
            help='Specifies size of MARC record shard, default is 100k'),
        )
    help = 'Runs multi-threaded indexer for bibliographic records into a Solr server'
    args = '[marc_file...]'

    def handle(self,*marc_file,**options):
        """
        Method takes an optional list of cores along with a MARC file or URL 
        and optional listing of cores.
        """
        cores = options.get('cores')
        if not cores:
            cores = ['marc_catalog']
        shard_size = options.get('shard_size')
        if not shard_size:
            shard_size = 100000
        # Creates shards 
        marc_records = []
        marc_reader = QuickMARCReader(open(marc_file,'r'))
        for row in marc_reader:
            marc_records.append(row)
        total_records = len(marc_records)
        total_shards = total_records / shard_size
        for shard in range(0,total_shards):
            for core in cores:
                marc_records_queue.add({'records':marc_records[(shard*shard_size):(shard*shard_size + shard_size)],
                                        'solr_url':solr_urls[core]})
                    

        

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
         chunk = self.file_handle.read(int(first5) - 5)
         yield first5 + chunk
         
                  

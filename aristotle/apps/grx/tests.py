"""
test.py - Unit tests for Gold Rush Django Application

(c) 2011 Colorado College
"""
__author__ = 'Jeremy Nelson'
import grx.settings as grx
from django.test import TestCase
from grx.bots.grxbots import GoldRushBot
from grx.bots.solrbots import SolrBot

class SetupTest(TestCase):

    def setUp(self):
        # Default bots used in this app
        self.default_solr_bot = SolrBot()
        self.default_grx_bot = GoldRushBot()

        # Set-up bots from settings
        self.solr_bot = SolrBot(solr_server=grx.SOLR_URL)
        self.grx_bot = GoldRushBot(institutional_code=grx.INSTITUTIONAL_CODE)
        

    def test_solr_setup(self):
        # Test default for solr bot
        self.assertEqual(self.default_solr_bot.solr_server,
                         'http://0.0.0.0:8983/solr')
        # Test grx solr bot
        self.assertEqual(self.solr_bot.solr_server,
                         grx.SOLR_URL)
        self.assertEqual(self.solr_bot.cache_location,
                         'solr/solr_cache')

    def test_goldrush_setup(self):
        # Test default grx bot
        self.assertEqual(self.default_grx_bot.inst_code,
                         '001_CCL')

        # Test grx bot
        self.assertEqual(self.grx_bot.inst_code,
                         grx.INSTITUTIONAL_CODE)
        

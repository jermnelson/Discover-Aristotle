"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from bots.solrbots import SolrBot

class SolrBotTest(TestCase):

    def setUp(self):
        self.default_bot = SolrBot()

    def test_default_setup(self):
        """
        Tests that default bot solr URL.
        """
        self.assertEqual(self.default_bot.solr_server,
                         'http://0.0.0.0:8983/solr')
        self.assertEqual(self.default_bot.cache_location,
                         'solr/solr_cache')


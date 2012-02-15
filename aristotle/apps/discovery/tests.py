"""
 :mods:`tests` Unit tests for discovery functionality in Aristotle
"""
__author__ = 'Jeremy Nelson'
import unittest
from django.test.client import Client

class TestSearch(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    
    def test_default(self):
        response = c.get('/')
        self.assertEquals(response.status_code,'200') 

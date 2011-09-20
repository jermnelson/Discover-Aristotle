#
# models.py - Gold Rush Microservices 
#
__author__ = 'Jeremy Nelson'

from django.db import models

class DatabaseNameStemmer(models.Model):
    """DatabaseNameStemmer class matches a value and returns a normalized name
       of a database to query Solr"""
    last_updated = models.DateTimeField('last updated',
                                        auto_now_add=True)
    database_name = models.CharField(max_length=150)
    starts_with = models.CharField(max_length=50)
    

class Subject(models.Model):
    """Subject class is listing of Subject that we use to query Gold Rush"""
    last_updated = models.DateTimeField('last updated',
                                        auto_now_add=True)
    name = models.CharField(max_length=200)

 

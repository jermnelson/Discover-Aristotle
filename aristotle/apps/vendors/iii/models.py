"""
 models.py - Django models for interacting with III Millennium System
"""
__author__ = 'Jeremy Nelson'

from eulxml import xmlmap
from django.db import models


class IIIRecord(xmlmap.XmlObject):
    """
    Base class for III XML records extracted from calls to Millennium
    WebOPAC irecord.
    """
    creation_date = xmlmap.StringField('/IIIRECORD/RECORDINFO/CREATEDATE')
    last_updated = xmlmap.StringField('/IIIRECORD/RECORDINFO/LASTUPDATEDATE')
    previous_updated = xmlmap.StringField('/IIIRECORD/RECORDINFO/PREUPDATEDATE')
    record_key = xmlmap.StringField('/IIIRECORD/RECORDINFO/RECORDKEY')
    revisions = xmlmap.IntegerField('/IIIRECORD/RECORDINFO/REVISIONS')

class ItemRecord(IIIRecord):
    """
    Millennium XML item records
    """
    due_date = xmlmap.StringField("/IIIRECORD/TYPEINFO/ITEM/FIXFLD[FIXLABEL[.='DUE DATE']]/FIXVALUE")
    location_code = xmlmap.StringField("/IIIRECORD/TYPEINFO/ITEM/FIXFLD[FIXLABEL[.='LOCATION']]/FIXVALUE")
    status = xmlmap.StringField("/IIIRECORD/TYPEINFO/ITEM/FIXFLD[FIXLABEL[.='STATUS']]/FIXVALUE")
    volume = xmlmap.StringField("/IIIRECORD/VARFLD[HEADER/TAG[.='VOLUME']]/FIELDDATA")

class IIIStatusCode(models.Model):
    """
    Stores III Item status codes
    """
    code = models.CharField(max_length=5)
    value = models.CharField(max_length=20)

class Fund(models.Model):
    """
    Stores full number and a code for a look-up from a order record value.
    """
    code = models.CharField(max_length=10)
    value = models.CharField(max_length=25)

class FundProcessLog(models.Model):
    """
    Keeps track of each time an order record CSV file is processed to expand
    fund short code to full value.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    substitutions = models.IntegerField()

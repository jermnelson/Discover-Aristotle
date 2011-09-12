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
    status = xmlmap.StringField("/IIIRECORD/TYPEINFO/ITEM/FIXFLD[FIXLABEL[.='STATUS']]/FIXVALUE")
    volume = xmlmap.StringField("/IIIRECORD/TYPEINFO/ITEM/VARFLD[HEADER/TAG[.='VOLUME']]/FIELDDATA")

class IIIStatusCode(models.Model):
    """
    Stores III Item status codes
    """
    code = models.CharField(max_length=5)
    value = models.CharField(max_length=20)

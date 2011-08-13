from django.db import models
from eulxml import xmlmap

class IIIRecord(xmlmap.XmlObject):
    """
    Base class for III XML records extracted from calls to Millennium
    WebOPAC irecord.
    """
    creation_date = xmlmap.StringField('RECORDINFO/CREATEDATE')
    last_updated = xmlmap.StringField('RECORDINFO/LASTUPDATEDATE')
    previous_updated = xmlmap.StringField('RECORDINFO/PREUPDATEDATE')
    record_key = xmlmap.StringField('RECORDINFO/RECORDKEY')
    revisions = xmlmap.IntegerField('RECORDINFO/REVISIONS')

class ItemRecord(IIIRecord):
    """
    Millennium XML item records
    """
    status = xmlmap.IntegerField('RECORDINFO/REVISIONS')
    
    

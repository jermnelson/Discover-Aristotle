from eulxml import xmlmap

class IIIRecord(xmlmap.XmlObject):
    """
    Base class for III XML records extracted from calls to Millennium
    WebOPAC irecord.
    """
    creation_date = xmlmap.StringField('IIIRECORD/RECORDINFO/CREATEDATE')
    last_updated = xmlmap.StringField('IIIRECORD/RECORDINFO/LASTUPDATEDATE')
    previous_updated = xmlmap.StringField('IIIRECORD/RECORDINFO/PREUPDATEDATE')
    record_key = xmlmap.StringField('IIIRECORD/RECORDINFO/RECORDKEY')
    revisions = xmlmap.IntegerField('IIIRECORD/RECORDINFO/REVISIONS')

class ItemRecord(IIIRecord):
    """
    Millennium XML item records
    """
    due_date = xmlmap.StringField("TYPEINFO/BIBLIOGRAPHIC/FIXFLD[FIXLABEL[.='DUE DATE']]/FIXVALUE")
    status = xmlmap.IntegerField("TYPEINFO/BIBLIOGRAPHIC/FIXFLD[FIXLABEL[.='STATUS']]/FIXNUMBER")

"""
  :mod:`repository.models` Module contains models using Django and Eulfedora
  to manipulate and extract objects from the  Fedora Repository 
"""

from django.db import models
from eulfedora.models import DigitalObject,FileDatastream,XmlDatastream
from eulxml.xmlmap import mods
import settings

class ADRBasicContentModel(DigitalObject):
    """
     `ADRBasicContentModel` models the ADR Basic Content Model
    """
    ADRBASIC_CONTENT_MODEL = 'info:fedora/%s' % settings.FEDORA_ADRBASICMODEL
    CONTENT_MODELS = [ ADRBASIC_CONTENT_MODEL ]
    mods = XmlDatastream("MODS",
                         "MODS XML datastream",
                         defaults={'versionable': True})

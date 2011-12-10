"""
  :mod:`repository.models` Module contains models using Django and Eulfedora
  to manipulate and extract objects from the  Fedora Repository 
"""

from django.db import models
from django.contrib.auth.models import User
import settings

class RepositoryMovementLog(models.Model):
    """
    :class:`RepositoryMovementLog` logs PID movement within the Fedora 
    Commons Digital Repository
    """
    collection_pid = models.CharField(max_length=30)
    created_on = models.DateField(auto_now_add=True)
    source_pid = models.CharField(max_length=30)

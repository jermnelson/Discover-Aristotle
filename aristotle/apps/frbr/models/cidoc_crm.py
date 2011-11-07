#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2009,2010,2011 Jeremy Nelson, Tomichi Informatics LLC
#
"""
:mod:`frbr.models.cidoc_crm` Supports the classes and relationships required
by `frbr.models.frbr_oo` modules. This module eventually be extended to
support of entire CIDOC CRM specification.

Specifications
--------------

    * _CIDOC CRM: http://www.cidoc-crm.org/docs/cidoc_crm_version_5.0.3.pdf
"""
__author__ = 'Jeremy Nelson'
__version__ = '0.1.1'

import datetime,os
import logging
from django.db import models
from django.contrib.contenttypes.models import ContentType
from djanog.contrib.contenttypes import generic
 

class PropositionalObject(models.Model):
    """
    _`CIDOC CRM` PropositionalObject page. 34
    
    This class comprises immaterial items, including but not limited to
    stories, plots, procedural prescriptions, algorithms, laws of physics
    or images that are, or represent in some sense, sets of propositions
    about real or imaginary things and that are documented as single units
    or serve as topic of discourse. 
    """
    created_by = generic.GenericForeignKey('content-type','object_id')
    created_on = models.DateTimeField(auto_now_add=True)


class Person(models.Model):
    """
    _`CIDOC CRM` PropositionalObject page. 11

    This class comprises real persons who live or are assumed to have lived.
    """
    created_by = generic.GenericForeignKey('content-type','object_id')
    created_on = models.DateTimeField(auto_now_add=True)

class Type_relations(models.Model):
    TYPE_ROLE = (
        (1,_("has broader term"),
         2,_("has narrower term"),
         3,_("has type"))
        )
    Type = models.ForeignKey("Type")
    entity = generic.GenericForeignKey('content-type','object_id')
    role = models.PostiveIntegerField(choices=TYPE_ROLES,
                                      default=None)    

class Type(models.Model):
    """
    _`CIDOC CRM` PropositionalObject page. 24
    
    This class comprises concepts denoted by terms from thesauri and controlled
    vocabularies used to characterize and classify instances of CRM classes
    """
    text = models.CharField(max_length=100)
    
    
    

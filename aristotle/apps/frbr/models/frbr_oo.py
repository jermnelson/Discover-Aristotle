"""
 frbr_oo.py - Migrated FRBR data models from eCataloger to Aristotle
"""
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
'''
:mod:`frbr.models.frbr` classes for modeling bibliographic records
as IR entities as described in the current versions of
`FRBR <http://www.ifla.org/publications/functional-requirements-for-bibliographic-records>`_
and extending using object-orientated
`FRBRoo <http://www.cidoc-crm.org/frbr_inro.html>`_ enabling support for both
bibliographic and museum information.

Specifications
--------------

    * _FRBR: http://www.ifla.org/files/cataloguing/frbr/frbr_2008.pdf
    * _FRBRoo: http://www.cidoc-crm.org/docs/frbr_oo/frbr_docs/FRBRoo_V1.0.1.pdf
'''
__author__ = 'Jeremy Nelson'
__version__ = '0.1.1' 

import datetime,os
import logging
from django.db import models
from django.contrib.contenttypes.models import ContentType
from djanog.contrib.contenttypes import generic
from frbr.models import cidoc_crm

#=============================================================================#
# FRBR Models                                                                 #
#=============================================================================#
FULL_ESTABLISHED,PROVISIONAL,PRELIMINARY = 1,2,3

IDENTIFICATION_STATUS = (
    (FULL_ESTABLISHED,_("Fully established"),
     PROVISIONAL,_("Provisional"),
     PRELIMINARY,_("Preliminary"))
    )

AUTHORITY_CODES = (
    (1,_("NAF"),
     2,_("SANB"))
    )


class audience_relations(models.Model):
    MARC_ROLES = (
        (1,_('Adolescent'),
         2,_('Adult'),
         3,_('General'),
         4,_('Juvenile'),
         5,_('Pre-Adolescent'),
         6,_('Preschool'),
         7,_('Primary'),
         8,_('Specialized'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    role = models.PostiveIntegerField(choices=MARC_ROLES,
                                      default=None)

class work_members(models.Model):
    work = generic.GenericForeignKey('content-type','object_id')
    member = generic.GenericForeignKey('content-type','object_id')

class work_relations(models.Model):
    WORK_ROLE = (
        (1,_('Creator'),
         2,_('Consulted Source'),
         3,_('Content Coverage'),
         4,_('Distinguishing Characteristic'),
         5,_('Identifier'),
         6,_('Note'),
         7,_('Subject'),
         8,_('Title'),
         9,_('Treaty_signatory'))
        )
    work = models.ForeignKey('Work')
    entity = generic.GenericForeignKey('content-type','object_id')
    role = models.PostiveIntegerField(choices=WORK_ROLES,
                                      default=None)
         

class work_subjects(models.Model):
    """ Subject can be another Work, Expression, Manifestation, Item,
    Person, Corporate Body, Concept, Object, Event, or Place"""
    work = models.ForeignKey('Work')
    subject = generic.GenericForeignKey('content-type','object_id')


class Work(cidoc_crm.PropositionalObject):
    """ A distinct intellectual or artistic creation. A work is an abstract
        entity; there is no single material object one can point to as the
        work.
        FRBR specification pg. 17
    """
    context = models.TextField(null=True,
                               blank=False)
    derivative = models.ForeignKey('self',blank=True)
    earliest_date = BaseDateProperty()
    epoch = generic.GenericForeignKey('content-type','object_id')
##    form = models.Property(required=False,
##                             choices=(["biography",
##                                       "braille",
##                                       "concerto",
##                                       "direct electronic",
##                                       "drawing",
##                                       "electronic",
##                                       "essay",
##                                       "large print",
##                                       "map",
##                                       "microfiche",
##                                       "microfilm",
##                                       "microopaque",
##                                       "novel",
##                                       "online",
##                                       "painting",
##                                       "photograph",
##                                       "play",
##                                       "poem",
##                                       "regular print",
##                                       "serial",
##                                       "sonata",
##                                       "symphony"]))
    
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    is_marctarget = model.NullBooleanField()
    intended_termination = models.DateField(blank=True)
    nature_of_content = models.TextField(blank=True)
    organization_system = models.TextField(blank=True)
    place_of_origin = generic.GenericForeignKey('content-type','object_id')
    realized = models.ForeignKey('SelfContainedExpression',
                                 blank=True)
    representive = models.ForeignKey('Expression',
                                     blank=True)
    successor = models.ForeignKey('self',blank=True)
    



class ComplexWork(Work):
    ''' FRBRoo specification of a Complex Work.'''

    def is_member_of(self,work):
        query = work_members.objects.filter(work=work).filter(member=self)
        if query:
            return True
        return False
        

    def has_member(self,work):
        query = work_members.objects.filter(work=self).filter(member=work)
        if query:
            return True
        return False


class ContainerWork(Work):
    ''' FRBRoo specification of a multiple works "enhance or add value to
        expressions from one or more other works without altering them, by
        the selection, arrangement and/or addition of features of different
        form, such as layout to words, recitation and movement to texts,
        instrumentation to musical scores etc." (6/2009 draft, pg.44)'''
    
    def get_works(self):
        query = work_members.objects.filter(work=work)
        return query


class IndividualWork(Work):
    ''' FRBRoo specification of an Individual work for works that
        "are realized by one and only one self-contained expression.
        (FRBR spec, pg. 43)'''

    def save(self):
        if self.realized is None:
            raise ValueError("IndividualWork.realized must be "\
                             "SelfContainedExpression")
        if not isinstance(self.realized,SelfContainedExpression):
            raise ValueError("IndividualWork.realized must be "\
                             "SelfContainedExpression, realized "\
                             "is a %s" % type(self.realized))
        return super(Work,self).save()
    
                                       

class AggregationWork(Work):
    ''' FRBRoo specification of an aggregation work "essence is the selection
        and/or arrangement of expressions of one or more other works.
        (pg. 45 6/2009 spec).'''
    members = db.ListProperty(db.Key,
                              default=None)

    def get_members(self):
        return self.get_collection(property_name='members')

    def put(self):
        for member in self.get_members():
            if str(member.__class__).lower() == str(ContainerWork).lower() or\
               str(member.__class__).lower() == str(IndividualWork).lower():
                pass
            else:
                raise db.BadValueError("All member Works in an AggregationWork "\
                                       "instance must be either a ContainerWork "\
                                       "or IndividualWork, member class is %s" %\
                                       (str(type(member))))
        return super(Work,self).put()
                                       

class PublicationWork(ContainerWork):
    ''' FRBRoo specification for a PublicationWork, for "works that have
        been planned to result in a manifestation product type and that
        pertain to the rendering of expressions from other works."
        (pg.45,46 6/2009 spec.)'''

    def put(self):
        if self.form:
            publication_forms = ["biography",
                                 "essay",
                                 "novel",
                                 "play",
                                 "poem",
                                 "serial"]
            if not publication_forms.count(self.form):
                raise db.BadValueError("PublicationWork.form must be: %s\n"\
                                       " instance form is %s" %\
                                       (publication_forms,self.form))
        return super(ContainerWork,self).put()
    

class SerialWork(ComplexWork,PublicationWork):
    ''' FRBRoo specification of a Serial Work as works that "works that are,
        or have been, planned to result in sequences of manifestations
        with common features." (pg.45 6/2009 spec.)'''
    has_issuing_rule = db.ReferenceProperty(collection_name='work_design_or_procedure')

    def put(self):
        if not self.form:
            self.form = "serial"
        # Check to see all works are also members
        for work_key in self.works:
            if not self.members.count(work_key):
                self.members.append(work_key)
        return super(PublicationWork,self).put()

class PerformanceWork(ContainerWork):
    ''' FRBRoo specification of a PerformanceWork, a work that "comprises
        the sets of concepts for rendering a particular or a series of like
        performances." (pg.46  6/2009 spec.)'''

    def put(self):
        if self.is_realized_in():
            expression = self.is_realized_in()
            if not isinstance(expression,PerformancePlan):
                raise db.BadValueError("PerformanceWork.realized expression "\
                                       "must be a PerformancePlan, realized "\
                                       "class is %s" % type(expression))
        return super(ContainerWork,self).put()

class RecordingWork(ContainerWork):
    ''' FRBRoo specification of a RecordingWork a work "conceptualise the
        capturing of features of perdurants." (pg.46 6/2009 spec.)'''
    composition_forms = db.StringListProperty()

    def put(self):
        if self.is_realized_in():
            expression = self.is_realized_in()
            if not isinstance(expression,Recording):
                raise db.BadValueError("RecordingWork.realized expression "\
                                       "must be a Recording, expression class "\
                                       " is %s" % type(self.expression))
        return super(ContainerWork,self).put()

class CartographicWork(ContainerWork):
    ''' Models a work such as a map.'''
    coordinates = db.GeoPtProperty()
    all_coordinates = db.ListProperty(db.Key,
                                      default=None)
    equinox = BaseDateProperty()
    right_ascension = db.StringProperty()
    declination = db.StringProperty()

    def put(self):
        if not self.form:
            self.form = 'map'
        return db.Model.put(self)

class DissertationThesisWork(ContainerWork):
    ''' Models a dissertation or thesis as a work, following RDA pg.5
        <http://www.rdaonline.org/Work_6_1_09.pdf> for special work.'''
    type = db.StringProperty(required=True,
                             choices=(["dissertation",
                                       "thesis"]))
    degree_granted = BaseDateProperty()
    academic_degree = db.StringProperty()
    granting_body = db.ReferenceProperty()

class ShippingListWork(ContainerWork):
    """ Base class for federal and Colorado state shipping lists.
    """
    processed_by = db.UserProperty()
    processed_on = db.DateProperty()
    list_date = db.DateProperty()
    number = db.StringProperty(required=True)


class FederalShippingListWork(ShippingListWork):
    """ Models a federal document shipping list, all individual items
        contained in the shipping list are included as IndividualWorks
        in this class "works" property."""
    type_of = db.StringProperty(required=True,
                                choices=(["print",
                                          "microfiche",
                                          "electronic",
                                          "blm",
                                          "dod",
                                          "forest service",
                                          "other"]))
        
class ColoradoShippingListWork(ShippingListWork):
    """ Models a Colorado document shipping list, all individual items
        contained in this shipping list are IndividualWorks in the class.
    """
    type_of = db.StringProperty(required=True,
                                choices=(["standard",
                                          "stateLINC",
                                          "other"]))

    

class MusicalWork(Work):
    composition_forms = db.StringListProperty()
    key_of = db.StringProperty()
    # Medium values come from page 2<http://www.rdaonline.org/Work_6_1_09.pdf>
    medium = db.StringProperty(required=False,
                               choices=(["piano strings: piano trio",
                                         "piano strings: piano quartet",
                                         "piano strings: piano quintet",
                                         "strings trio",
                                         "strings quartet",
                                         "woodwind quartet",
                                         "keyboard instrument",
                                         "continuo",
                                         "organs (2)",
                                         "pianos (2), 8 hands",
                                         "pianos (2)",
                                         "piano, 4 hands",
                                         "piano",
                                         "brasses",
                                         "instrumental ensemble",
                                         "keyboard instruments",
                                         "percussion",
                                         "plucked instruments",
                                         "strings",
                                         "winds",
                                         "woodwinds",
                                         "orchestra",
                                         "string orchestra",
                                         "alto",
                                         "baritone",
                                         "base",
                                         "mezzo-soprano",
                                         "soprano",
                                         "tenor",
                                         "men's solo voices",
                                         "mixed solo voices",
                                         "women's solo voices",
                                         "men's voices",
                                         "mixed voices",
                                         "unison voices",
                                         "women's voices",
                                         "accompanied",
                                         "unaccompanied",
                                         "band"]))
    numeric = NumericProperty()

class person_events(models.Model):
    event = generic.GenericForeignKey('content-type','object_id')
    person = models.ForeignKey('Person')

class person_names(models.Model):
    NAME_ROLES = (
        (1,_('Given'),
         2,_('Middle'),
         3,_('Family'),
         4,_('Former Family'),
         5,_('Title or Terms of Address'),
         6,_('Suffix'),
         8,_('Nickname'))
        )
    person = models.ForeignKey('Person')
    role = models.PostiveIntegerField(choices=MARC_ROLES,
                                      default=None)
    text = models.CharField(max_length=100)

class person_relations(models.Model):
    PERSON_ROLES = (
        (1,_('Address'),
         2,_('Affiliation'),
         3,_('Description'),
         4,_('Identifier'),
         5,_('Notes'),
         6,_('Professional Field'),
         7,_('Occupation'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    person = models.ForeignKey('Person')
    role = models.PostiveIntegerField(choices=MARC_ROLES,
                                      default=None)
    
         
class Person(BaseModel):
    '''Agent models information specific to a person including
       names, important dates (birth, death), and other information.

       Also includes <http://www.rdaonline.org/Person_6_1_09.pdf>
       and 
       
    '''
    GENDER_ROLES = (
        (1,_("Female"),
         2,_("Male"),
         3,_("Transgender"),
         4,_("Not Known"))
        )
    active_end_period = models.DateProperty(default=None)
    active_start_period = models.DateProperty(default=None)
    authority = models.PostiveIntegerField(choices=AUTHORITY_CODES,
                                           default=None)
##    birth = models.DateField(default=None)
##    birth_location = generic.GenericForeignKey('content-type','object_id')
##    death = models.DateField(default=None)
##    death_location = generic.GenericForeignKey('content-type','object_id')
    gender = models.PostiveIntegerField(choices=GENDER_ROLES,
                                        default=None)
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    

class corporate_body_relations(models.Model):
    CORPORATE_ROLES = (
        (1,_('Associated Institution'),
         2,_('Code'),
         3,_('Description'),
         4,_('Identifier'),
         5,_('Note'),
         6,_('Place'),
         7,_('URL'))
        )
    corporate_body = models.ForeignKey('CorporateBody')
    entity = generic.GenericForeignKey('content-type','object_id')
    role = models.PostiveIntegerField(choices=CORPORATE_ROLES)
         

class CorporateBody(models.Model):
    '''Models a corporate body

    '''
    CORPORATE_TYPES = (
        (1,_('Corporate'),
         2,_('Non-profit'),
         3,_('Higher Education'),
         4,_('K-12 School'),
         5,_('Ad hoc'))
        )
    address = generic.GenericForeignKey('content-type','object_id')
    authority_rating = models.FloatField(default=None)
    authority = models.PostiveIntegerField(choices=AUTHORITY_CODES,
                                           default=None)     
    dissolution_date = models.DateField(default=None)
    held_on = models.DateField(default=None)
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
        
    incorporation_date = models.DateField(default=None)
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=50)
    type = models.PostiveIntegerField(choices=CORPORATE_TYPES,
                                      default=1)


class concept_relations(models.Model):
    CONCEPT_ROLES = (
        (1,_('Child concept'),
         2,_('Note'),
         3,_('Parent concept'),
         4,_('Subject'))
        )
    concept = models.ForeignKey('Concept')
    entity = generic.GenericForeignKey('content-type','object_id')
    role = models.PostiveIntegerField(choices=CONCEPT_ROLES)

class concept_terms(models.Model):
    TERM_ROLES = (
        (1,_('Preferred'),
         2,_('Varient'))
        )
    concept = models.ForeignKey('Concept')
    text = models.CharField(max_length=100)

class Concept(models.Model):
    '''Models a concept by associating a MODS subject model instance
       with children and parents relationships.
    '''
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)



class frbr_object_relations(models.Model):
    FRBR_OBJECT_ROLES = (
        (1,_('Identifier'),
         2,_('Note'),
         3,_('Source consulted'),
         4,_('Term'))
        )
    frbr_object = models.ForeignKey('FRBRObject')
    entity = generic.GenericForeignKey('content-type','object_id')
    role =  models.PostiveIntegerField(choices=FRBR_OBJECT_ROLES)
    
class FRBRObject(models.Model):
    ''' Models a FRBR Object

    '''
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    
##    
##
##    def get_identifiers(self):
##        return self.get_collection(property_name="identifiers")
##
##    def get_notes(self):
##        return self.get_collection(property_name="notes")
##
##    def get_sources_consulted(self):
##        return self.get_collection(property_name="sources_consulted")
##
##    def get_terms(self):
##        return self.get_collection(property_name="terms")


class place_relations(models.Model):
    PLACE_ROLES = (
        (1,_('City'),
         2,_('Code'),
         3,_('Coordinate'),
         4,_('Identifier'),
         5,_('Note'),
         6,_('Source consulted'),
         7,_('Term'))
        )
    place = models.ForeignKey('Place')
    entity = generic.GenericForeignKey('content-type','object_id')
    role =  models.PostiveIntegerField(choices=PLACE_ROLES)


class Place(BaseModel):
    '''
       Models a place
    '''
    PRIMARY,SECONDARY,OTHER = 1,2,3
    PLACE_CHOICES = (
        (1,_("Primary"),
         2,_("Secondary"),
         3,_("Other"))
        )
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    
    type_of = models.PositiveIntegerField(choices=PLACE_CHOICES,
                                          default=PRIMARY)
    postal_address = models.CharField(max_length=255,default=None)
    name = models.CharField(max_length=120)
    description = models.TextField(default=None)
    
##
##    def get_identifiers(self):
##        return self.get_collection(property_name="identifiers")
##
##    def get_notes(self):
##        return self.get_collection(property_name="notes")
##
##    def get_sources_consulted(self):
##        return self.get_collection(property_name="sources_consulted")

class event_relations(models.Model):
    EVENT_ROLES = (
        (1,_('Description'),
         2,_('Held at'),
         3,_('Identifier'),
         4,_('Note'),
         5,_('Source consulted'),
         6,_('Term'))
        )
    event = models.ForeignKey('Event')
    entity = generic.GenericForeignKey('content-type','object_id')
    role =  models.PostiveIntegerField(choices=EVENT_ROLES)
    
class Event(models.Model):
    '''Models an event.'''
    CONFERENCE,EVENT = 1,2
    EVENT_TYPES = (
        (CONFERENCE,_('Conference'),
         EVENT,_('Event'))
        )
    authority = models.PostiveIntegerField(choices=AUTHORITY_CODES,
                                           default=None)
    name = models.CharField(max_length=255)
    held_on = models.DateField(default=None)
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    type_of = models.PositiveIntegerField(chocies=EVENT_TYPES,
                                          default=EVENT)


##    def get_description(self):
##        return self.get_collection(property_name="description")
##
##    def get_identifiers(self):
##        return self.get_collection(property_name="identifiers")
##
##    def get_notes(self):
##        return self.get_collection(property_name="notes")
##
##    def get_sources_consulted(self):
##        return self.get_collection(property_name="sources_consulted")


class expression_creation_relations(models.Model):
    EXPRESSION_CREATION_ROLES = (
        (1,_('Created by'),
         2,_('Realization'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    expression_creation = models.ForeignKey('ExpressionCreation')
    role = models.PostiveIntegerField(choices=EVENT_ROLES)

class ExpressionCreation(Event):
    ''' FRBRoo class, class comprises activities that result in instances
        of F2 Expression coming into existence. This class characterises
        the externalisation of an Individual Work. (pg.50 6/2009 spec.)'''
    

    def was_created_by(self):
        pass
##        if self.expression and self.manifestation_singleton:
##            return (self.expression,self.manifestation_singleton)
##        elif self.expression and not self.manifestation_singleton:
##            return self.expression
##        elif not self.expression and self.manifestation_singleton:
##            return self.manifestation_singleton
##        else:
##            return None

##    def was_realized_through(self):
##        if self.realisation:
##            return self.realisation
##        else:
##            return None


class publication_event_relations(models.Model):
    PUBLICATION_EVENT_ROLES = (
        (1,_('Created through'),
         2,_('Realized through'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    publication_event = models.ForeignKey('PublicationEvent')
    role = models.PostiveIntegerField(choices=PUBLICATION_EVENT_ROLES)
    

class PublicationEvent(ExpressionCreation):
    ''' FRBRoo class, class comprises the activities of publishing.
        Such an event includes the creation of an F24 Publication Expression
        and setting up the means of production. (FRBRoo pg.52)'''
    

    def was_created_through(self):
        pass
##        if self.created:
##            return self.created
##        else:
##            return None

    def was_realised_through(self):
        pass
##        if self.realised:
##            return self.realised
##        else:
##            return None

class recording_event_relations(models.Model):
    RECORDING_EVENT_ROLES = (
        (1,_('Created through'),
         2,_('Recorded'),
         3,_('Realized through'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    recording_event = models.ForeignKey('RecordingEvent')
    role = models.PostiveIntegerField(choices=RECORDING_EVENT_ROLES)
                                   

class RecordingEvent(ExpressionCreation):
    ''' FRBRoo class, comprises activities that intend to convey (and preserve)
       the content of events in a recording, such as a live recording of a
       performance, a documentary, or other capture of a perdurant.
       (pg.51)'''
    
    def was_created_through(self):
        pass
##        if self.created:
##            return self.created
##        else:
##            return None

    def was_recorded_through(self):
        pass
##        if self.recorded:
##            return self.recorded
##        else:
##            return None

    def was_realized_through(self):
        pass
##        if self.realization:
##            return self.realization
##        else:
##            return None
    

class carrier_production_event_relations(models.Model):
    CARRIER_PRODUCTION_EVENT_ROLES = (
        (1,_('Produced by'),
         2,_('Produced things of type')
         3,_('Source for'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    carrier_production_event = models.ForeignKey('CarrierProductionEvent')
    role = models.PostiveIntegerField(choices=CARRIER_PRODUCTION_EVENT_ROLES)
    
class CarrierProductionEvent(Event):
    ''' FRBRoo class, comprises activities that result in instances of F5 Item
        coming into existence. The creation of a new copy of a file on an
        electronic carrier is also regarded as a Carrier Production Event.
        (pg. 52 6/2009 spec.)'''

    def get_produced_types(self):
        pass
    

    def get_source_material(self):
        pass

    def was_produced_by(self):
        pass

    def was_used_by(self):
        pass


class reproduction_event_relations(models.Model):
    REPRODUCTION_EVENT_ROLES = (
        (1,_('Produced by'),
         2,_('Reproduced by'))
        )
    entity = generic.GenericForeignKey('content-type','object_id')
    reproduction_event = models.ForeignKey('reproduction_event')
    role = models.PostiveIntegerField(choices=CARRIER_PRODUCTION_EVENT_ROLES)

class ReproductionEvent(Event):
    ''' FRBRoo class, E84 Information Carrier (such as an F5 Item or an
        F4 Manifestation Singleton which is also instance of
        E84 Information Carrier), preserving the expression carried by it.
        (pg.53)'''
    produced = db.ListProperty(db.Key,
                               default=None)
    reproduced = db.ListProperty(db.Key,
                                 default=None)


    def was_reproduced_by(self):
        if self.reproduced:
            return self.get_reproduced()
        else:
            return None

class expression_relations(models.Model):
    EXPRESSION_ROLES = (
        (1,_('Award'),
         2,_('Consulted source'),
         3,_('Context'),
         4,_('Distingushing characteristic'),
         5,_('Extent'),
         6,_('Form'),
         7,_('Genre'),
         8,_('Identifier'),
         9,_('Illustrative content'),
         10,_('Language'),
         11,_('Performer'),
         12,_('Realized by'),
         13,_('Summarization'),
         14,_('Supplementary'),
         15,_
    
class Expression(models.Model):
    ''' The intellectual or artistic realization of a work in the form
        of alpha-numeric, musical, or choreographic notation, sound,
        image, object, movement, etc., or any combination of such forms.

        RDA <http://www.rdaonline.org/Expression_6_1_09.pdf>
    '''
    ISSUANCES = (
        (1,_("Continuing"),
         2,_("Monographic"))
        )
    SOUND_CONTENTS = (
        (1,_("Sound"),
         2,_("Silent"))
        )
    TACTILE_NOTATIONS = (
        (1,_("Braille code"),
         2,_("Computing braille code"),
         3,_("Mathematics braille code"),
                                                   "mode code",
                                                   "music braille code",
                                                   "tactile graphic",
                                                   "tactile musical notation"
    critical_response = models.TextField(default=None)
    earliest_date = models.DateField(default=None)
    form = db.StringProperty(required=False,
                             choices=(["alpha-numeric notation",
                                       "cartographic dataset",
                                       "cartographic",
                                       "cartographic moving image",
                                       "cartographic tactile image",
                                       "cartographic image",
                                       "cartographic tactile three-dimensional form",
                                       "cartographic three-dimensional form",
                                       "computer dataset",
                                       "computer program",
                                       "dance",
                                       "mixed material",
                                       "mime",
                                       "moving image",
                                       "musical notation",
                                       "musical sound",
                                       "notated movement",
                                       "notated music",
                                       "other",
                                       "performed music",
                                       "photographic image",
                                       "sculpture",
                                       "sounds",
                                       "spoken word",
                                       "still image",
                                       "tactile image",
                                       "tactile notated music",
                                       "tactile notated movement",
                                       "tactile text",
                                       "tactile three-dimensional form",
                                       "text",
                                       "three-dimensional form",
                                       "three-dimensional moving image",
                                       "two-dimensional moving image",
                                       "unspecified",
                                       "software, multimedia",                                       
                                       "sound recording-musical",
                                       "sound recording-nonmusical",
                                       "three dimensional object",
                                       "url"]))
    
    identification_status = models.PostiveIntegerField(choices=IDENTIFICATION_STATUS,
                                                       default=PRELIMINARY)
    is_collection = db.BooleanProperty()    
    is_extensible = db.BooleanProperty()
    is_manuscript = db.BooleanProperty()    
    is_revisable = db.BooleanProperty()
    issuance = db.PositiveIntegerField(choices=ISSUANCE_CHOICES,
                                       default=None)
    movement_notation = db.StringProperty(required=False,
                                          choices=(["action stroke dance",
                                                    "beauchamp-feuillet",
                                                    "benesh movement",
                                                    "dance writing",
                                                    "eshkol-wachman",
                                                    "game play",
                                                    "labanotation",
                                                    "stepanov",
                                                    "other"]))
    
    script = db.StringProperty(required=False,
                               choices=(["Arab",
                                         "Armi",
                                         "Armn",
                                         "Avst",
                                         "Bali",
                                         "Bamu",
                                         "Batk",
                                         "Beng",
                                         "Blis",
                                         "Bopo",
                                         "Brah",
                                         "Brai",
                                         "Bugi",
                                         "Buhd",
                                         "Cakm",
                                         "Cans",
                                         "Cari",
                                         "Cham",
                                         "Cher",
                                         "Cirt",
                                         "Copt",
                                         "Cprt",
                                         "Cyrl",
                                         "Cyrs",
                                         "Deva",
                                         "Dsrt",
                                         "Egyd",
                                         "Egyh",
                                         "Egyp",
                                         "Ethi",
                                         "Geor",
                                         "Geok",
                                         "Glag",
                                         "Goth",
                                         "Grek",
                                         "Gujr",
                                         "Guru",
                                         "Hang",
                                         "Hani",
                                         "Hano",
                                         "Hans",
                                         "Hant",
                                         "Hebr",
                                         "Hira",
                                         "Hmng",
                                         "Hrkt",
                                         "Hung",
                                         "Inds",
                                         "Ital",
                                         "Java",
                                         "Jpan",
                                         "Kali",
                                         "Kana",
                                         "Khar",
                                         "Khmr",
                                         "Knda",
                                         "Kore",
                                         "Kthi",
                                         "Lana",
                                         "Laoo",
                                         "Latf",
                                         "Latg",
                                         "Latn",
                                         "Lepc",
                                         "Limb",
                                         "Lina",
                                         "Linb",
                                         "Lisu",
                                         "Lyci",
                                         "Lydi",
                                         "Mand",
                                         "Mani",
                                         "Maya",
                                         "Mero",
                                         "Mlym",
                                         "Moon",
                                         "Mong",
                                         "Mtei",
                                         "Mymr",
                                         "Nkgb",
                                         "Nkoo",
                                         "Ogam",
                                         "Olck",
                                         "Orkh",
                                         "Orya",
                                         "Osma",
                                         "Perm",
                                         "Phag",
                                         "Phli",
                                         "Phlp",
                                         "Phlv",
                                         "Phnx",
                                         "Plrd",
                                         "Prti",
                                         "Qaaa",
                                         "Qabx",
                                         "Rjng",
                                         "Roro",
                                         "Runr",
                                         "Samr",
                                         "Sara",
                                         "Sarb",
                                         "Saur",
                                         "Sgnw",
                                         "Shaw",
                                         "Sinh",
                                         "Sund",
                                         "Sylo",
                                         "Syrc",
                                         "Syre",
                                         "Syrj",
                                         "Syrn",
                                         "Tagb",
                                         "Tale",
                                         "Talu",
                                         "Taml",
                                         "Tavt",
                                         "Telu",
                                         "Teng",
                                         "Tfng",
                                         "Tglg",
                                         "Thaa",
                                         "Thai",
                                         "Tibt",
                                         "Ugar",
                                         "Vaii",
                                         "Visp",
                                         "Xpeo",
                                         "Xsux",
                                         "Yiii",
                                         "Zinh",
                                         "Zmth",
                                         "Zsym",
                                         "Zxxx",
                                         "Zyyy",
                                         "Zzzz"]))
    sound_content = models.PositiveIntergerField(default=None,
                                                 choices=SOUND_CONTENTS)
    
    tactile_notation = db.StringProperty(required=False,
                                         choices=(["braille code",
                                                   "computing braille code",
                                                   "mathematics braille code",
                                                   "mode code",
                                                   "music braille code",
                                                   "tactile graphic",
                                                   "tactile musical notation"]))
    title = db.ReferenceProperty(MODSData.titleInfo,
                                 collection_name="ExpressionTitle")
    use_restrictions = db.ListProperty(db.Key,default=None)
    urls = db.ListProperty(db.Key,
                           default=None)
    work = db.ReferenceProperty(Work,
                                collection_name="realized_work")

    def get_languages(self):
        return self.get_collection(property_name="languages")

    def get_use_restrictions(self):
        return self.get_collection(property_name="use_restrictions")

    def get_consulted_sources(self):
        return self.get_collection(property_name="consulted_sources")

    def get_realized_by(self):
        return self.get_collection(property_name="realized_by")

    def get_summarizations(self):
        return self.get_collection(property_name="summarizations")

    def get_supplementary(self):
        return self.get_collection(property_name="supplementary")

    def get_illustrative_content(self):
        return self.get_collection(property_name="illustrative_content")

    def get_performers(self):
        return self.get_collection(property_name="performers")

    def get_context(self):
        return self.get_collection(property_name="context")

    def get_genre(self):
        return self.get_collection(property_name="genre")

    def get_extent(self):
        return self.get_collection(property_name="extent")

    def get_urls(self):
        return self.get_collection(property_name="urls")

    def put(self):
        if self.realized_by:
            for value_key in self.realized_by:
                entity = db.get(value_key)
                if not isinstance(entity,(Person,CorporateBody)):
                    raise db.BadValueError('Expression realized_by '
                                           ' must be a Person or '
                                           'CorporateBody value is %s' %
                                           (type(entity)))
        if not self.display_form:
            if self.title is not None:
                self.display_form = self.title.title
        return db.Model.put(self)
    
class Summarization(db.Model):
    ''' Supporting model for Expression '''
    type = db.StringProperty(required=True,
                             choices=(["abstract",
                                       "chapter headings",
                                       "parts",
                                       "songs",
                                       "summary",
                                       "synopsis",
                                       "table of contents"]))
    date = BaseDateProperty()
    values = db.ListProperty(db.Key,
                             default=None)

    def get_values(self):
        if self.values:
            output = list()
            for value_key in self.values:
                output.append(db.get(value_key))
            return output
        else:
            return None

    def put(self):
        if self.type == 'abstract':
            for value in self.values:
                entity = db.get(value)
                if not isinstance(entity,MODSData.abstract):
                    raise db.BadValueError('''Summarization values
                                           must all be abstracts instances''')
        return db.Model.put(self)

class Supplementary(BaseModel):
    ''' Supporting model for Expression.'''
    type_of = db.StringProperty(required=False,
                                choices=(["index",
                                          "bibliography",
                                          "appendix",
                                          "site-map"]))
    values = db.ListProperty(db.Key,
                             default=None)

    def get_values(self):
        return self.get_collection(property_name="values")

class IllustrativeContent(BaseModel):
    ''' Supporting model for Expression, based RDA Expression's illustrative
        content, page 5 <http://www.rdaonline.org/Expression_6_1_09.pdf>'''
    type_of = db.StringProperty(required=False,
                                choices=(["charts",
                                          "coats of arms",
                                          "facsimiles",
                                          "forms",
                                          "genealogical tables",
                                          "illuminations",
                                          "illustration",
                                          "illustrations",
                                          "maps",
                                          "music",
                                          "phonodisc, phonowire, etc.",
                                          "photographs",
                                          "plans",
                                          "plates",
                                          "portraits",
                                          "samples"]))
    creators = db.ListProperty(db.Key,default=None)
    details = db.StringListProperty()

    def get_creators(self):
        return self.get_collection(property_name="creators")

class SelfContainedExpression(Expression):
    ''' FRBRoo specification of a SelfContainedExpression class that
        "comprises the immaterial realisations of individual works at
        a particular time that are regarded as a complete whole."
        (pg.47 6/2009 spec.)'''
    incorporated = db.ReferenceProperty(collection_name="incorporate_expression")

    def is_incorporated_in(self):
        if self.incorporated:
            return self.incorporated
        else:
            return None
        
class ExpressionFragment(Expression):
    ''' FRBRoo specification of an ExpressionFragment that "comprises parts of
        Expressions and these parts are not Self-contained Expressions
        themselves." (pg. 47 6/2009 spec.)'''
    fragment_parts = db.ListProperty(db.Key,
                                   default=None)
    

    def get_fragments(self):
        return self.get_collection(property_name='fragment_parts')

    def has_fragment(self,expression):
        if self.fragment_parts.count(expression.key()):
            return True
        else:
            return False

    def put(self):
        for expression in self.get_fragments():
            if isinstance(expression,SelfContainedExpression):
                raise db.BadValueError("ExpressionFragment parts cannot be "\
                                       "SelfContainedExpressions")
        return super(Expression,self).put()

class PerformancePlan(SelfContainedExpression):
    ''' Models FRBRoo's PerformancePlan expression as defined as "sets of
        directions to which individual performances of theatrical,
        choreographic, or musical works and their combinations should conform."
        (pg.49 6/2009 spec.)'''
    design = db.ReferenceProperty(collection_name="design_or_procedure")

class PublicationExpression(SelfContainedExpression):
    ''' Models FRBRoo's PublicationExpression that is "comprises the complete
        layout and content provided by a publisher (in the broadest sense of
        the term) in a given publication and not just what was added by the
        publisher to the authors' expressions." (pg. 48 6/2009 spec.)'''
    constituents = db.ListProperty(db.Key,
                                   default=None)

    def get_constituents(self):
        return self.get_collection(property_name="constituents")

    def put(self):
        if self.is_incorporated_in():
            if not self.constituents.count(self.incorporated.key()):
                self.constituents.append(self.incorporated.key())
        return super(SelfContainedExpression,self).put()

class Recording(SelfContainedExpression):
    ''' Models FRBRoo's Recording expression that "comprises expressions
        which are created in instances of F29 Recording Event. A recording
        is intended to convey (and preserve) the content of one or more
        events." (pg.49 48 6/2009 spec.)'''
    events = db.ListProperty(db.Key,
                             default=None)

    def get_events(self):
        return self.get_collection(property_name="events")
    
class Serial(PublicationExpression):
    '''A periodical models a periodic publication, can be a magazine, 
       journal, newspaper, or series in either physical or digital forms

    '''
    frequency = db.StringProperty(required=True,
                                  choices=(["annual",
                                            "bimonthly",
                                            "semiweekly",
                                            "daily",
                                            "biweekly",
                                            "semiannual",
                                            "biennial",
                                            "triennial",
                                            "three times a week",
                                            "three times a month",
                                            "continuously updated",
                                            "monthly",
                                            "quarterly",
                                            "semimonthly",
                                            "three times a year",
                                            "weekly",
                                            "completely irregular"]))
    is_current_subscription = db.BooleanProperty()
    issn = db.ReferenceProperty(MODSData.identifier,
                                collection_name="issn_id")
    issnl = db.ReferenceProperty(MODSData.identifier,
                                 collection_name="link_issn")
    online_issn = db.ReferenceProperty(MODSData.identifier,
                                       collection_name="issn_online")
    publisher = db.ReferenceProperty(CorporateBody)
    sequencing_pattern = db.StringProperty()

    def put(self):
        if not self.issuance:
            self.issuance = "continuing"
        if self.issn:
            if self.issn.type != 'issn':
                raise db.BadValueError("Serial.issn type must be issn not %s" %\
                                       self.issn.type)
        if self.online_issn:
            if self.online_issn.type != 'issn':
                raise db.BadValueError("Serial.online_issn type must be issn not %s" %\
                                       self.online_issn.type)
        if self.work:
            if not isinstance(self.work,SerialWork):
                raise db.BadValueError("Serial.work must be a SerialWork "\
                                       "instance, work's class is %s" %\
                                       self.work.__class__)
        return super(PublicationExpression,self).put()

class CartographicImageObject(Expression):
    """ This class models either a cartographic image or object

    """
    geodetic_measurement = db.StringProperty()
    grid_measurement = db.StringProperty()
    
    presentation_technique = db.StringProperty(required=False,
                                               choices=(["anaglyphic",
                                                         "diagrammatic",
                                                         "pictorial"]))
    projection = db.StringProperty(required=False,
                                   choices=(["azimuthal equidistant",
                                             "transverse mercator"]))
    
    scale = db.StringProperty(required=False,
                              choices=(["angular",
                                        "horizontal",
                                        "other",
                                        "vertical"]))
    scale_measurement = db.StringProperty()
    vertical_measurement = db.StringProperty()

    def put(self):
        if self.form:
            if not (self.form=="cartographic" or
            self.form == "cartographic moving image" or
            self.form == "cartographic tactile image" or
            self.form == "cartographic image"):
                raise db.BadValueError("CartographicImageObject form "\
                                       "cannot be %s" % self.form)
        else:
            self.form = "cartographic image"
        return db.Model.put(self)


class Graphic(Expression):
    ''' A grapic models a born digital or physical graphic
        Colour content from page 8
        <http://www.rdaonline.org/Expression_6_1_09.pdf>.
    '''
    colour_content = db.StringProperty(required=False,
                                       choices=(["black and white",
                                                 "gray scale",
                                                 "tinted",
                                                 "toned",
                                                 "tinted and toned",
                                                 "sepia"]))
    technique = db.StringProperty(required=False,
                                  choices=(["born digital",
                                            "engraving"]))

class Legal(Expression):
    ''' Models an expression of a legal work, from RDA Expression
        <http://www.rdaonline.org/Expression_6_1_09.pdf> pg.2.'''
    protocols = db.StringListProperty()
    
class MusicalNotation(Expression):
    ''' A musical notation models an expression of a music
        notation. Includes RDA Other Distinguishing Characteristics
        of the Expression of a Musical Work for type_of, from page 2
        of <http://www.rdaonline.org/Expression_6_1_09.pdf>.
    '''
    duration = DurationProperty()
    format_of = db.StringProperty(required=False,
                                  choices=(["choir book",
                                            "chorus score",
                                            "condensed score",
                                            "part",
                                            "piano conductor part",
                                            "piano score",
                                            "study score",
                                            "table book",
                                            "violin conductor part",
                                            "vocal score"]))
    notation_form = db.StringProperty(required=False,
                                      choices=(["graphic notation",
                                                "letter notation",
                                                "neumatie notation",
                                                "number notation",
                                                "staff notation",
                                                "tablature",
                                                "tonic sol-fa",]))
    medium_of_performance = db.StringProperty()
    type_of = db.StringProperty(required=False,
                                choices=(["accompaniment reduced for keyboard",
                                          "arranged",
                                          "chorus",
                                          "chorus score",
                                          "chorus scores",
                                          "close score",
                                          "condensed score",
                                          "condensed score or piano-conductor score",
                                          "full score",
                                          "full score, miniature or study size",
                                          "libretto",
                                          "librettos",
                                          "multiple score formats",
                                          "not applicable",
                                          "other",
                                          "performer-conductor part",
                                          "short score",
                                          "sketches",
                                          "text",
                                          "texts",
                                          "unknown",
                                          "vocal score",
                                          "vocal scores",
                                          "voice score"]))    

    def put(self):
        if self.form:
            if not (self.form == "musical notation" or
            self.form == "notated music"):
                raise db.BadValueError("MusicalNotation.form %s not valid" %\
                                       self.form)
        else:
            self.form = "musical notation"
        return db.Model.put(self)


class ProjectedImage(Expression):
    '''A projected images models a moving images. Includes RDA enhanced
       properties from <http://www.rdaonline.org/Expression_6_1_09.pdf>
       page 5.
    '''
    artistic_credits = db.ListProperty(db.Key,default=None)
    aspect_ratio = db.StringProperty(required=False,
                                     choices=(["full screen",
                                               "wide screen",
                                               "mixed"]))
    colour_content = db.StringProperty(required=False,
                                       choices=(["black and white",
                                                 "tinted",
                                                 "toned",
                                                 "tinted and toned",
                                                 "sepia"]))
    date_captured = BaseDateProperty()
    duration = DurationProperty()
    technique = db.StringProperty(required=False,
                                  choices=(["animation",
                                            "computer generation",
                                            "live action",
                                            "3D"]))
    technical_credits = db.ListProperty(db.Key,default=None)
    where_captured = db.ReferenceProperty()

    def get_artistic_credits(self):
        return self.get_collection(property_name="artistic_credits")

    def get_technical_credits(self):
        return self.get_collection(property_name="technical_credits")

    def get_credits(self):
        all_credits = self.get_artistic_credits() + self.get_technical_credits()
        return all_credits


class Religious(Expression):
    ''' Models an expression of a religious work, from RDA Expression
        <http://www.rdaonline.org/Expression_6_1_09.pdf> pg.2.'''
    confraternity = db.ReferenceProperty(CorporateBody,
                                         collection_name="confraternity")
    douai = db.ReferenceProperty(CorporateBody,
                                 collection_name="douai")

class RemoteSensingImage(Expression):
    ''' A remote sensing image models an expression of an image
        captured through remote sensing instrument.

    '''
    colour_content = db.StringProperty(required=False,
                                       choices=(["black and white",
                                                 "gray scale",
                                                 "tinted",
                                                 "toned",
                                                 "tinted and toned",
                                                 "sepia"]))
    recording_technique = db.StringProperty(required=False,
                                            choices=(["infrared line scanning",
                                                      "multispectral photography",
                                                      "passive microwave mapping",
                                                      "SLAR"]))
    special_characteristics = db.ListProperty(db.Key,default=None)

class Manifestation(BaseModel):
    reformating_qualities = ['access',
                             'preservation',
                             'replacement']
    acquisition_sources = db.ListProperty(db.Key,
                                          default=None)
    access_authorization_sources = db.ListProperty(db.Key,
                                                   default=None)
    access_restrictions = db.ListProperty(db.Key,
                                          default=None)
    availability_terms = db.StringListProperty()
    captured_on = BaseDateProperty()
    classifications = db.ListProperty(db.Key,
                                      default=None)
    copyright_date = BaseDateProperty()
    digital_origin = db.StringProperty(required=False,
                                       choices=(["born digital",
                                                 "reformatted digital",
                                                 "digitized microfilm",
                                                 "digitized other analog"]))
    distribution_date = BaseDateProperty()
    distributors = db.ListProperty(db.Key,
                                   default=None)
    edition = db.StringProperty()
    expressions = db.ListProperty(db.Key,
                                  default=None)
    extent = db.ListProperty(db.Key,
                             default=None)
    fabricators = db.ListProperty(db.Key,
                                  default=None)
    forms_of_carrier = db.ListProperty(db.Key,
                                       default=None)
    identifiers = db.ListProperty(db.Key,
                                  default=None)
    issuance_mode = db.StringProperty(required=False,
                                      choices=(["single unit",
                                                "multipart monograph",
                                                "serial",
                                                "integrating resource"]))
    manufacturers = db.ListProperty(db.Key,
                                    default=None)
    materials = db.ListProperty(db.Key,
                                default=None)
    media_type = db.StringProperty(required=False,
                                   choices=(["audio",
                                             "computer",
                                             "microform",
                                             "microscopic",
                                             "stereographic",
                                             "projected",
                                             "unmediated",
                                             "video",
                                             "other",
                                             "unspecified"]))
    modified_on = BaseDateProperty()
    notes = db.ListProperty(db.Key,
                            default=None)
    parallel_titles = db.ListProperty(db.Key,
                                      default=None)
    physical_mediums = db.StringListProperty(default=None)
    place_of_distribution = db.ReferenceProperty(Place,
                                                 collection_name="manifest_pod")
    place_of_publication = db.ListProperty(db.Key,
                                           default=None)
    popularity = db.RatingProperty()
    produced_by = db.ListProperty(db.Key,
                                  default=None)
    production_places = db.ListProperty(db.Key,
                                  default=None)
    publisher = db.ReferenceProperty(CorporateBody,
                                     collection_name="manifest_publisher")
    publication_date = BaseDateProperty()
    publication_date_start = BaseDateProperty()
    publication_date_end = BaseDateProperty()
    reformating_quality = db.StringListProperty()
    statement_of_responsibility = db.ListProperty(db.Key,
                                                  default=None)
    series = db.ListProperty(db.Key,
                             default=None)
    terms_of_availability = db.ListProperty(db.Key,
                                            default=None)
    title = db.ReferenceProperty(MODSData.titleInfo,
                                 collection_name="a_manifest_title")
    use_restrictions = db.ListProperty(db.Key,
                                       default=None)
    varient_titles = db.ListProperty(db.Key,
                                     default=None)
    valid_on = BaseDateProperty()


    def get_extent(self):
        return self.get_collection(property_name="extent")

    def get_forms_of_carrier(self):
        return self.get_collection(property_name="forms_of_carrier")
    
    def get_access_restrictions(self):
        return self.get_collection(property_name='access_restrictions')
 

    def get_callnumbers(self):
        return self.get_collection(property_name="classifications")
    
    def get_classifications(self):
        return self.get_collection(property_name='classifications')

    def get_expressions(self):
        return self.get_collection(property_name="expressions")

    def get_identifiers(self):
        return self.get_collection(property_name="identifiers")


    def get_materials(self):
        return self.get_collection(property_name="materials")

    def get_notes(self):
        return self.get_collection(property_name="notes")

    def get_parallel_titles(self):
        return self.get_collection(property_name='parallel_titles')

    def get_publication_places(self):
        return self.get_collection(property_name="place_of_publication")

    def get_series(self):
        return self.get_collection(property_name='series')

    def get_statement_of_responsibility(self):
        return self.get_collection(property_name="statement_of_responsibility")

    def get_use_restrictions(self):
        return self.get_collection(property_name="use_restrictions")

    def get_varient_titles(self):
        return self.get_collection(property_name='varient_titles')

    def put(self):
        if not self.display_form and self.title:
            self.display_form = self.title.title
        if self.produced_by:
            for producer_key in self.produced_by:
                entity = db.get(producer_key)
                if not isinstance(entity,(Person,CorporateBody)):
                    raise db.BadValueError('Manifestation produced_by must '
                                           'a Person or CorporateEntity '
                                           'instances, type is %s' %
                                           (type(entity),))
        if self.expressions:
            for expression_key in self.expressions:
                entity = db.get(expression_key)
                if not isinstance(entity,Expression):
                    raise db.BadValueError('Manifestation expressions must '
                                           'all be Expression instances, '
                                           'expression\'s type is %s' %
                                           (type(entity),))

        if self.reformating_quality:
            for quality in self.reformating_quality:
                # Should raise index error if quality is not in list.
                self.reformating_qualities[quality]
        return db.Model.put(self)


class MaterialInfomation(BaseModel):
    ''' Supporting models of Manifestation.'''
    applied = db.StringProperty(required=False,
                                choices=(["mixed materials",
                                          "acrylic paint",
                                          "chalk",
                                          "charcoal",
                                          "crayon",
                                          "dye",
                                          "gouache",
                                          "graphite",
                                          "ink",
                                          "oil paint",
                                          "pastel",
                                          "plaster",
                                          "tempura",
                                          "water colour"]))
    base = db.StringProperty(required=False,
                             choices=(["bristol board",
                                       "canvas",
                                       "cardboard",
                                       "ceramic",
                                       "glass",
                                       "hard board",
                                       "illustration board",
                                       "ivory",
                                       "leather",
                                       "metal",
                                       "paper",
                                       "parchment",
                                       "plaster",
                                       "plastic",
                                       "porcelain",
                                       "shellac",
                                       "skin",
                                       "stone",
                                       "synthetic",
                                       "textile",
                                       "vellum",
                                       "vinyl",
                                       "wax",
                                       "wood"]))


class ManifestationSingleton(Manifestation):
    ''' FRBRoo class that comprises physical objects that each carry an instance of F2
        Expression, and that were produced as unique objects, with no siblings
        intended in the course of their production. (pg. 29 6/2009 spec.)'''

    def put(self):
        if len(self.expressions) > 1:
            raise db.BadValueError("ManifestationSingleton can only have one "\
                                   " expression. Total expression for this "\
                                   "instance are %s" % len(self.expressions))
        return super(Manifestation,self).put()
                                   
class HandPrintedBook(Manifestation):
    ''' Models a hand-printed book.'''
    book_format = db.StringProperty(required=False,
                                    choices=(["folio",
                                              "4to",
                                              "8v0",
                                              "12 mo",
                                              "16 mo",
                                              "24 mo",
                                              "32 mo",
                                              "48 mo",
                                              "64 mo"]))
    collation = db.StringProperty()
    foliation = db.StringProperty()

class Manuscript(ManifestationSingleton):
    ''' Models a manuscript using RDA Manifestation
        <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf> pg. 22'''
    production_method = db.StringProperty(required=False,
                                          choices=(["holograph",
                                                    "manuscript",
                                                    "printout",
                                                    "carbon copy",
                                                    "photocopy",
                                                    "transcript",
                                                    "handwritten",
                                                    "typewritten"]))

class CartographicResource(Manifestation):
    ''' Models a RDA cartographic resource, from page 19,
        <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf>.'''
    extent_type = db.StringProperty(required=False,
                                    choices=(["atlas",
                                              "diagram",
                                              "globe",
                                              "map",
                                              "model",
                                              "profile",
                                              "remote sensing image",
                                              "section",
                                              "view"]))
    is_plural = db.BooleanProperty()
    layout = db.StringProperty(required=False,
                               choices=(["both sides",
                                         "back to back"]))
    
class Microform(Manifestation):
    '''Models a microform. Carrier values come from
      <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf> page 3

    '''
    carrier = db.StringProperty(required=False,
                                choices=(["aperture card",
                                          "microfiche",
                                          "microfiche cassette",
                                          "microfilm cartridge",
                                          "microfilm cassette",
                                          "microfilm reel",
                                          "microfilm roll",
                                          "microfilm slip",
                                          "microopaque"]))
    emulsion = db.StringProperty(required=False,
                                 choices=(["diazo",
                                           "mixed",
                                           "silver halide",
                                           "vesicular"]))
    generation = db.IntegerProperty()
    polarity = db.IntegerProperty()
    reduction_ratio = ReductionRatioProperty()

class Periodical(Manifestation):
    ''' Differs from FRBR specification as Serial can both be an Expression
        or a Manifestation. To differ between a Serial Expression vs a
        Serial Manifestation, will model a Periodical as a Serial Manifestation.
        Will make implementation easier.

        Includes RDA numbering of serials 
        <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf> pgs.4
    '''
    alphanumeric_first_designation = db.StringProperty()
    alphanumeric_last_designation = db.StringProperty()
    chronological_first_designation = db.StringProperty()
    chronological_last_designation = db.StringProperty()    
    issue = db.StringProperty()
    is_supplement = db.BooleanProperty(default=False)
    is_most_current = db.BooleanProperty(default=False)
    publication_status = db.StringProperty(required=True,
                                           choices=(["current",
                                                     "ceased"]))
    volume = db.StringProperty()

class PrintedBook(Manifestation):
    """ Models a printed book

    """
    isbn = db.ReferenceProperty(MODSData.identifier)
    type_face = db.StringProperty()
    type_size = db.StringProperty()
    rda_font_size = db.StringProperty(required=False,
                                      choices=(["large print",
                                                "giant print"]))

    def put(self):
        if self.isbn:
            if self.isbn.type != 'isbn':
                raise db.BadValueError("PrintedBook.isbn is not an ISBN"\
                                       " identifier, type is %s instead" %\
                                       self.isbn.type)
        return super(PrintedBook,self).put()

class SoundRecording(Manifestation):
    ''' Models a sound recording. Carrier values come from
      <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf> page 3

    '''
    carrier = db.StringProperty(required=False,
                                choices=(["audio cartridge",
                                          "audio cylinder",
                                          "audio disc",
                                          "audio roll",
                                          "audiocassette",
                                          "audiotape reel",
                                          "sound-track reel"]))
    kind_of_cutting = db.StringProperty(required=False,
                                        choices=(["lateral",
                                                  "vertical"]))
    kind_of_sound = db.StringProperty(required=False,
                                      choices=(["monaural",
                                                "stereophonic",
                                                "quadraphonic"]))
    groove_width  = db.StringProperty()
    playing_speed = db.StringProperty()
    playback_channels = db.IntegerProperty()
    recording_type = db.StringProperty(required=False,
                                       choices=(["analog",
                                                 "digital"]))
    recording_medium = db.StringProperty(required=False,
                                         choices=(["magnetic tape",
                                                   "optical disc",
                                                   "born digital"]))
    special_playback_characteristics = db.StringListProperty()
    special_reproduction_characteristic = db.StringProperty(required=False,
                                                            choices=(["DBX",
                                                                      "Dolby",
                                                                      "NAB"]))
    tape_configuration=db.StringProperty()
    
    

class VisualProjection(Manifestation):
    ''' Models visual projection

    '''
    broadcast_standard = db.StringProperty()
    carrier = db.StringProperty(required=False,
                                choices=(["film cartridge",
                                          "film cassette",
                                          "film reel",
                                          "filmslip",
                                          "filmstrip",
                                          "filmstrip cartridge",
                                          "online resource",
                                          "overhead transparency slide",
                                          "stereograph card",
                                          "stereographic disc",
                                          "video cartridge",
                                          "videocassette",
                                          "videodisc",
                                          "videotape reel"]))
    generation = db.IntegerProperty()
    polarity = db.StringProperty(required=False,
                                 choices=(["positive",
                                           "negative",
                                           "mixed"]))
    presentation_format = db.StringProperty(required=False,
                                            choices=(["beta",
                                                      "blu-ray",
                                                      "dvd",
                                                      "hd-dvd",
                                                      "vhs",
                                                      "x-shockwave-flash"]))
    regional_encoding = db.ReferenceProperty(MODSData.hierarchicalGeographic,
                                             collection_name="regional_encoding")
    video_format = db.StringProperty()

class NotatedMusic(Manifestation):
    ''' Models Notated Music following RDA Manifestation page.20
        <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf>'''
    extent_type = db.StringProperty(required=False,
                                    choices=(["score",
                                              "condensed score",
                                              "study score",
                                              "piano conductor part",
                                              "violin conductor part",
                                              "vocal score",
                                              "piano score",
                                              "chorus score",
                                              "choir book",
                                              "table book"]))
    is_plural = db.BooleanProperty()
    layout = db.StringProperty(required=False,
                               choices=(["bar by bar",
                                         "bar over bar",
                                         "line by line",
                                         "line over line",
                                         "melody chord system",
                                         "open score",
                                         "outline",
                                         "paragraph",
                                         "section by section",
                                         "short form scoring",
                                         "single line",
                                         "vertical score"]))

class ElectronicResource(Manifestation):
    ''' Models an electronic resource

    '''
    carrier = db.StringProperty(required=False,
                                choices=(["computer card",
                                          "computer chip cartridge",
                                          "computer disc",
                                          "computer disc cartridge",
                                          "computer tape cartridge",
                                          "computer tape cassette",
                                          "computer tape reel"]))
    encoding_format = db.StringProperty()
    file_requirements = db.ListProperty(db.Key,default=None)
    system_requirements = db.ListProperty(db.Key,default=None)

class Image(ElectronicResource):
    ''' Models an image. Colours, resolution, and kilobytes all
        come from RDA Manifestation page 19
        <http://www.rdaonline.org/Manifestation_6_1_09-1.pdf>'''
    colours = db.StringListProperty(default=None)
    resolution = db.StringProperty()
    kilobytes = db.FloatProperty()

class RemoteAccessElectronicResource(Manifestation):
    """ Models an remote access electronic resource

    """
    access_address = db.ReferenceProperty(MODSData.url,
                                          collection_name="resource_url")
    mode_of_access = db.StringProperty(required=True,
                                       choices=(["internet",
                                                 "www",
                                                 "restricted"]))
    internet_media_type = db.StringProperty()
    is_trial = db.BooleanProperty()
    is_subscription = db.BooleanProperty()
    proxy_address = db.ReferenceProperty(MODSData.url,
                                         collection_name="proxy_url")
    transmission_speed = db.StringProperty()

#==============================================================================#
# Custom FRBR Manifestation Classes for Government Publications                #
#==============================================================================#
class GovernmentPublication(Manifestation):
    """ Models a generic Government publication using controlled vocabulary
    from MARC 008 Books
    <http://www.loc.gov/marc/bibliographic/bd008b.html>
    """
    pub_type = db.StringProperty(required=False,
                                choices=(['autonomous or semi-autonomous',
                                          'federal/national',
                                          'government publication-level undetermined',
                                          'international intergovernmental',
                                          'local',
                                          'multilocal',
                                          'multistate',
                                          'other',
                                          'state, etc.',
                                          'unknown']))

    

class FederalDocument(GovernmentPublication):
    """Models a United States Federal Document"""
    number = db.ReferenceProperty(MODSData.classification,
                                  collection_name="sudoc_callnumber")
    sudoc_item_number = db.StringProperty()
    shipping_lists = db.ListProperty(db.Key)

    def get_lists(self):
        """ returns shipping lists associated with this document. Most
            documents are only associated with a single shippiing list,
            however, documents can appear on multiple lists (i.e.
            once on Paper and then on a Separate."""
        return self.get_collection(property_name="shipping_lists")

    def put(self):
        """ put call sets parent pub_of property to federal/national if
        not set"""
        if not self.pub_type:
            self.pub_type = 'federal/national'
        return super(GovernmentPublication,self).put()
        

class FederalMediaDocument(FederalDocument):
    """ Models a CD-ROM, DVD, or other electronic meda format document."""
    format = db.StringProperty(required=False,
                               choices=(['cdrom',
                                         'dvd',
                                         'floppy',
                                         'other']))

class FederalMicroficheDocument(FederalDocument,Microform):
    """ Models a federal microfiche document. """
    total_items = db.IntegerProperty()

class ColoradoDocument(GovernmentPublication):
    """ Models a Colorado State Document"""
    number = db.ReferenceProperty(MODSData.classification,
                                  collection_name="codoc_callnumber")
    shipping_lists = db.ListProperty(db.Key)
    format = db.StringProperty(required=False,
                               choices=(["paper",
                                         "CD-ROM",
                                         "DVD"]))

    def get_lists(self):
        """ returns list of Colorado Shipping Lists associated with this
            document."""
        return self.get_collection(property_name="shipping_lists")

    def put(self):
        """ put call sets parent pub_of property to state if not set"""
        if not self.pub_type:
            self.pub_type = "state, etc."
        return super(GovernmentPublication,self).put()
    
class Item(BaseModel):
    ''' Item is the lowest level of description of a physical object in
         the FRBR context.

    '''
    access_restrictions = db.ListProperty(db.Key,default=None)
    barcode = db.ReferenceProperty(MODSData.identifier)
    condition = db.StringProperty()
    exhibition_history = db.ListProperty(db.Key,default=None)
    fingerprint = db.StringProperty()
    identifiers = db.ListProperty(db.Key,default=None)
    inscriptions = db.ListProperty(db.Key,default=None)
    is_missing = db.BooleanProperty(default=False)
    location = db.ReferenceProperty(MODSData.location,
                                    collection_name="item_location")
    manifestation = db.ReferenceProperty(Manifestation,
                                         collection_name="exemplified")
    marks = db.ListProperty(db.Key,default=None)
    usage = db.ListProperty(datetime.datetime,default=None)
    owned_by = db.ListProperty(db.Key,default=None)
    provenance = db.ListProperty(db.Key,default=None)
    scheduled_treatment = db.ListProperty(db.Key,default=None) 
    treatment_history = db.ListProperty(db.Key,default=None)

    def put(self):
        if self.barcode:
            if self.barcode.type != 'barcode':
                raise db.BadValueError("Item.barcode's type is not barcode "\
                                       "type is %s" % self.barcode.type)
        if not self.display_form:
            if self.manifestation.title.display_form:
                self.display_form = "%s ITEM" % self.manifestation.title.display_form
        return db.Model.put(self)

class Record(BaseModel):
    ''' Record is a supporting class for storing specific information about
        the creation of FRBR entities .'''
    changed_on = BaseDateProperty()
    creation_date = BaseDateProperty()
    description_conventions = db.ListProperty(db.Key,
                                              default=None)
    entities = db.ListProperty(db.Key,default=None)    
    identifiers = db.StringListProperty()
    language_cataloged_in = db.ReferenceProperty(\
        collection_name='langauge_of_cataloging')
    modifying_agencies = db.ListProperty(db.Key,
                                         default=None)
    org_cataloging_agency = db.ReferenceProperty(\
        collection_name='original_cataloging_agency')
    transcribing_agency = db.ReferenceProperty(\
        collection_name='transcribing_agency')

    def get_description_conventions(self):
        return self.get_collection(property_name='description_conventions')

    def get_modifying_agencies(self):
        return self.get_collection(property_name='modifying_agencies')
                                         

                                         
    
    

class Endeavor(BaseModel):
    ''' Endeavor is a base class representing a single
        Work-Expression-Manifestation-Item object all with 1:1
        relationships for derived objects. Also includes a title
        reference for queries.
    '''
    item = db.ReferenceProperty(Item,
                                collection_name='endeavor_item')
    title = db.ReferenceProperty(MODSData.titleInfo,
                                 collection_name='endeavor_title')

    def put(self):
        endeavor_key = db.Model.put(self)
        endeavor = db.get(endeavor_key)
        endeavor_search = EndeavorSearch(endeavor=endeavor)
        if hasattr(endeavor,'manifestation'):
            note_str = ''
            if self.manifestation.notes:
                for note in self.manifestation.get_notes():
                    note_str += str(note.value)
                endeavor_search.description = db.Text(note_str)
        if self.title:
            endeavor_search.title = self.title.title
        endeavor_search.put()
        return endeavor_key

class AudioEndeavor(Endeavor):
    ''' AlbumEndeavor creates an ER mapping for a song or other
        audio recording.'''
    work = db.ReferenceProperty(MusicalWork,
                                collection_name='audio_work')
    expression = db.ReferenceProperty(Expression,
                                      collection_name="audio_expression")
    manifestation = db.ReferenceProperty(SoundRecording,
                                         collection_name="audio_manifestation")
    

class DissertationEndeavor(Endeavor):
    ''' DissertationEndeavor creates an ER mapping for a Dissertation.'''
    work = db.ReferenceProperty(DissertationThesisWork,
                                collection_name='dissertation_work')
    expression = db.ReferenceProperty(Expression,
                                      collection_name='dissertation_expresion')
    manifestation = db.ReferenceProperty(Manifestation,
                                         collection_name='dissertation_manifestation')

    def put(self):
        if self.work:
            self.work.type = 'dissertation'
        return Endeavor.put(self)


class FilmEndeavor(Endeavor):
    ''' FilmEndeavor creates an ER mapping for projected film.'''
    work = db.ReferenceProperty(Work,
                                collection_name="film_work")
    expression = db.ReferenceProperty(ProjectedImage,
                                      collection_name="film_expression")
    manifestation = db.ReferenceProperty(VisualProjection,
                                         collection_name="film_manifestation")
    

class MapEndeavor(Endeavor):
    ''' MapEndeavor is a specific entity relationship that createas a FRBR
        Entity 1 association for representing a Map.'''
    work = db.ReferenceProperty(CartographicWork,
                                collection_name='map_cartographic_work')
    expression = db.ReferenceProperty(CartographicImageObject,
                                      collection_name=\
                                      'map_cartographic_image_object')
    manifestation = db.ReferenceProperty(CartographicResource,
                                         collection_name=\
                                         'map_cartographic_resource')

    def put(self):
        ''' Presets various entity properties to correspond to a map.'''
        if self.work:
            self.work.form = 'map'
        if self.manifestation:
            self.manifestation.extent_type = 'map'
        return Endeavor.put(self)

class PrintedBookEndeavor(Endeavor):
    ''' PrintedBookEndeavor creates an ER mapping for a printed book.'''
    work = db.ReferenceProperty(PublicationWork,
                                collection_name='printed_book_work')
    expression = db.ReferenceProperty(Expression,
                                      collection_name='printed_book_expression')
    manifestation = db.ReferenceProperty(PrintedBook,
                                         collection_name='printed_book_manifestation')

    def put(self):
        ''' Presets entity properties to correspond to a printed book'''
        if self.work:
            good_work_forms = ["novel",
                               "play",
                               "poem",
                               "essay",
                               "biography"]
            if not good_work_forms.count(self.work.form):
                raise db.BadValueError('PrintedBookEndeavor Work form must '\
                                       'be one of theses values: [%s], value '
                                       'is %s' % (good_work_forms,
                                                  self.work.form))
        if self.expression:
            if self.expression.form != 'text':
                self.expression.form = 'text'
        return Endeavor.put(self)

class PurchasedElectronicResourceEndeavor(Endeavor):
    ''' PurchasedElectronicResource creates an ER mapping for electronic
        databases or other resources that are purchased by an organization.'''
    work = db.ReferenceProperty(IndividualWork,
                                collection_name='purchased_electronic_resource_work')
    expression = db.ReferenceProperty(SelfContainedExpression,
                                      collection_name='purchased_electronic_resource_expression')
    manifestation = db.ReferenceProperty(RemoteAccessElectronicResource,
                                       collection_name='purchased_electronic_resource_manifestation')
    
    
       
class WebSiteEndeavor(Endeavor):
    ''' WebSiteEndeavor creates an ER mapping for a web-site.'''
    work = db.ReferenceProperty(IndividualWork,
                                collection_name="website_work")
    expression = db.ReferenceProperty(SelfContainedExpression,
                                      collection_name="website_expression")
    manifestation = db.ReferenceProperty(RemoteAccessElectronicResource,
                                         collection_name="website_manifestation")

    
    
    
        
  


#=============================================================================#
# FRBR Custom Validation                                                      #
#=============================================================================#
def workExists(work):
    ''' Function takes potential work, uses creator-title pairs to query for
        existing works. If any pair matches, returns existing key.'''
    creator_keys = work.creators
    title_keys = work.titles
    for creator_key in creator_keys:
        for title_key in title_keys:
            query_str = '''SELECT __key__ FROM Work WHERE creators=:1 AND
                           titles=:2'''
            query = db.GqlQuery(query_str,creator_key,title_key)
            existing_work_key = query.get()
            if existing_work_key:
                return existing_work_key
    
def personExists(person,tolerance=None):
    ''' Function takes potential person, queries based on given and family
        names. If matches and if tolerance exists, compares all
        properties between existing and potential person, if passes tolerance,
        assumes existing person and returns key, otherwise returns 
        existing person key. '''
    query = db.GqlQuery('''SELECT * FROM Person WHERE family=:1 AND
                           given=:2''',
                        person.family,person.given)
    existing_person = query.get()
    if existing_person:
        if tolerance:
            if compareModels(existing_person,person) >= tolerance:
                return existing_person.key()
        else:
            return existing_person.key()

def corporateBodyExists(corp_body,tolerance=None):
    ''' Function takes potential corporate body, queries datastore based on
        name of corporate body. If matches and passes existing
        tolerance, returns key of corporate body, otherwise returns nothing.'''
    query = db.GqlQuery('''SELECT * FROM CorporateBody WHERE name=:1''',
                        corp_body.name)
    existing_corp_body = query.get()
    if existing_corp_body:
        if tolerance:
            if compareModels(existing_corp_body,corp_body) >= tolerance:
                return existing_corp_body.key()
        else:
            return existing_corp_body.key()

def eventExists(event,tolerance=None):
    ''' Function takes potential event, queries datastore based on name of
        potential event. If matches and passes existing tolerance, returns
        key of matched event, otherwise returns nothing.'''
    query = db.GqlQuery('''SELECT * FROM Event WHERE name=:1''',
                        event.name)
    existing_event = query.get()
    if existing_event:
        if tolerance:
            if compareModels(existing_event,event) >= tolerance:
                return existing_event.key()
        else:
            return existing_event.key()

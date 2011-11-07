"""
  omm.py - Object Memory Modeling Python module
  
  http://www.w3.org/2005/Incubator/omm/XGR-omm-20111026/
  http://www.dfki.de/~haupert/files/omm_xg_sample.xsd
"""
__author__ = "Jeremy Nelson"
import datetime,re
from lxml import etree
import rdflib
from eulxml import xmlmap

class _BaseOMM(xmlmap.XmlObject):
    ROOT_NS = 'http://www.w3.org/2005/Incubator/omm/XGR-omm/'
    ROOT_NAMESPACES = { 'omm' : ROOT_NS,
                        'xml': "http://www.w3.org/1999/XML"}

class OMMElement(_BaseOMM):
    name = xmlmap.StringField('local-name(.)')
    text = xmlmap.StringField('.')

class date(OMMElement):
    ROOT_NAME = 'date'
    encoding = xmlmap.StringField('@omm:encoding')

class additionalBlocks(OMMElement):
    ROOT_NAME = 'additionalBlocks'
    omm_type = xmlmap.StringField("@omm:type")

class attribute(OMMElement):
    ROOT_NAME = 'attribute'
    key = xmlmap.StringField("@omm:key")

class attributeList(_BaseOMM):
    ROOT_NAME = 'attributeList'
    attributes = xmlmap.NodeListField('omm:attribute',
                                      attribute)

class contributor(OMMElement):
    ROOT_NAME = 'contributor'
    type_of = xmlmap.StringField('@omm:type')


class contribution(_BaseOMM):
    ROOT_NAME = "contribution"
    contributor = xmlmap.NodeField("omm:contributor",
                                contributor)
    date = xmlmap.NodeField('omm:date',
                            date)

class creator(OMMElement):
    ROOT_NAME = 'creator'
    type_of = xmlmap.StringField('@omm:type')

class creation(_BaseOMM):
    ROOT_NAME = 'creation'
    creator = xmlmap.NodeField('omm:creator',
                               creator)
    date = xmlmap.NodeField('omm:date',
                            date)

class description(OMMElement):
    ROOT_NAME = 'description'
    lang = xmlmap.StringField('@xml:lang')

class identifier(OMMElement):
    ROOT_NAME = 'identifier'
    type_of = xmlmap.StringField("@omm:type")

class identification(_BaseOMM):
    ROOT_NAME = 'identification'
    identifiers = xmlmap.NodeListField('omm:identifier',
                                       identifier)

class link(OMMElement):
    ROOT_NAME = 'link'
    hash_of = xmlmap.StringField("@omm:hash")
    type_of = xmlmap.StringField("@omm:type")

class omm_format(OMMElement):
    ROOT_NAME = 'format'
    encryption = xmlmap.StringField("@omm:encription")
    schema = xmlmap.StringField("@omm:schema")

class omm_element(OMMElement):
    ROOT_NAME = 'element'

class primaryID(OMMElement):
    ROOT_NAME = 'primaryID'
    omm_type = xmlmap.StringField("@omm:type")

class relation(OMMElement):
    ROOT_NAME = 'relation'
    relation_type = xmlmap.StringField('@omm:relationType')
    type_of = xmlmap.StringField('@omm:type')


class tag(_BaseOMM):
    ROOT_NAME = 'tag'
    value = xmlmap.StringField("@omm:value")
    tags = xmlmap.NodeListField('omm:tag',
                                'tag')
    type_of = xmlmap.StringField("@type")

    
class subject(OMMElement):
    ROOT_NAME = 'subject'
    tags = xmlmap.NodeListField('omm:tag',
                                tag)
    
class timeSpan(OMMElement):
    ROOT_NAME = 'timeSpan'
    begin = xmlmap.NodeField('omm:begin',
                             date)
    end = xmlmap.NodeField('omm:end',
                           date)

class structureInformation(_BaseOMM):
    ROOT_NAME = 'structureInformation'
    date = xmlmap.NodeField('omm:date',
                            date)
    relation = xmlmap.NodeField('omm:relation',
                                relation)
    time_span = xmlmap.NodeField('omm:timeSpan',
                                 timeSpan)

class structure(_BaseOMM):
    ROOT_NAME = 'structure'
    structure_information = xmlmap.NodeListField('omm:structureInformation',
                                                 structureInformation)

class title(OMMElement):
    ROOT_NAME = 'title'
    lang = xmlmap.StringField("@xml:lang")

# Container Elements

class header(_BaseOMM):
    ROOT_NAME = 'header'
    additionalBlocks = xmlmap.NodeListField('omm:additionalBlocks',
                                            additionalBlocks)
    version = xmlmap.StringField('omm:version')
    primaryID = xmlmap.NodeField('omm:primaryID',
                                 primaryID)

class toc(_BaseOMM):
    ROOT_NAME = 'toc'
    ID = xmlmap.StringField("@omm:id")
    creations = xmlmap.NodeListField('omm:creation',
                                     creation)
    elements = xmlmap.NodeListField('omm:element',
                                    omm_element)
    link = xmlmap.NodeField('omm:link',link)
    toc_namespace = xmlmap.StringField('omm:namespace')
    omm_format = xmlmap.NodeField('omm:format',
                                  omm_format)
    title = xmlmap.NodeField("omm:title",
                             title)
    
class payload(OMMElement):
    ROOT_NAME = 'payload'
    encoding = xmlmap.StringField("@omm:encoding")
    attributes = xmlmap.NodeField("omm:attributeList",
                                  attributeList)
    identification = xmlmap.NodeField("omm:identification",
                                      identification)
        
class block(_BaseOMM):
    ROOT_NAME = 'block'
    ID = xmlmap.StringField("@omm:id")
    contributions = xmlmap.NodeListField('omm:contribution',
                                         contribution)
    creations = xmlmap.NodeListField('omm:creation',
                                     creation)
    description = xmlmap.NodeField("omm:description",
                                   description)
    link = xmlmap.NodeField('omm:link',link)
    block_namespace = xmlmap.StringField('omm:namespace')
    payload = xmlmap.NodeField('omm:payload',
                               payload)
    omm_format = xmlmap.NodeField('omm:format',
                                  omm_format)
    title = xmlmap.NodeField("omm:title",
                             title)
    subjects = xmlmap.NodeListField('omm:subject',
                                    subject)    
    
class OMM(_BaseOMM):
    ROOT_NAME = 'omm'
    header = xmlmap.NodeField('omm:header',
                              header)
    toc = xmlmap.NodeField('omm:toc',
                           toc)
    blocks = xmlmap.NodeListField('omm:block',
                                  block)
     
    
    

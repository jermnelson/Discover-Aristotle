"""
 codebook.py - Data Documentation Initiative (DDI) Codebook Module
"""
__author__ = 'Jeremy Nelson'

from eulxml import xmlmap

DDILITE_NAMESPACE = "ddi:instance:3_0_CR3"
DDILIST_SCHEMA = "http://www.icpsr.umich.edu/DDI"


class Common(xmlmap.XmlObject):
    """DDILite class with DDI namespace declaration for all elements"""
    ROOT_NS = DDILITE_NAMESPACE
    ROOT_NAMESPACES = {"r":"ddi:reusable:3_1",
                       "xhtml":"http://www.w3.org/1999/xhtml",
                       "dc":"ddi:dcelements:3_1",
                       "a":"ddi:archive:3_1",
                       "g":"ddi:group:3_1",
                       "cm":"ddi:comparative:3_1",
                       "c":"ddi:conceptualcomponent:3_1",
                       "d":"ddi:datacollection:3_1",
                       "l":"ddi:logicalproduct:3_1",
                       "p":"ddi:physicaldataproduct:3_1",
                       "ds":"ddi:dataset:3_1",
                       "pi":"ddi:physicalinstance:3_1",
                       "m1":"ddi:physicaldataproduct_ncube_normal:3_1",
                       "m2":"ddi:physicaldataproduct_ncube_tabular:3_1",
                       "m3":"ddi:physicaldataproduct_ncube_inline:3_1",
                       "m4":"ddi:physicaldataproduct_proprietary:3_1",
                       "s":"ddi:studyunit:3_1",
                       "pr":"ddi:ddiprofile:3_1"}

class codeBook(Common):
    """
    ':class:`~datasets.ddi.codeBook` class for DDI Codebook Specification, 
    maps XML to Python objects using eulxml
    """
    XSD_SCHEMA = DDILITE_SCHEMA
    ROOT_NAME = 'codeBook'
   
    

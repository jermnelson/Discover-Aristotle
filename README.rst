README
======

Aristotle is an `Django <http://www.djangoproject.com/>`_-based 
bibliographic, repository, and access project. Unless explicitly stated, 
all software code and documentation, including any and intellectual property, 
is licensed under the `Apache 2 <http://www.apache.rog/licenses/LICENSE-2.0.html/>`_
open-source licence and/or `Creative Commons <http://creativecommons.org/>`_ 
copyright license.

Dependencies
------------

**aristotle** currently depends on

* `django <http://www.djangoproject.com/>`_
* `eulfedora <https://github.com/emory-libraries/eulfedora>`_ 
* `eulxml <https://github.com/emory-libraries/eulxml>`_ 
* `pymarc <https://github.com/tow/sunburnt>`_
* `sunburnt <https://github.com/edsu/pymarc>`_

Current and Future Django Applications
--------------------------------------

* :doc:`catalog` Default summary and detail views of Solr, FRBR, MARC, and Fedora commons objects with facets.
* :doc:`discovery` Forked Kochief discovery application, modified for use as the Discovery Interface for Aristotle.
* :doc:`datasets` Generic scientific, social science, and humanity dataset management for use by other applications.
* :doc:`etd`  Electronic Thesis and Dissertation Django application
* `FUTURE` frbr FRBR object-oriented models front-end to Cassandra, Postgres, or sqlite, or Google App Engine (requires additional modules)
* :doc:`grx`  Gold Rush XML microservices application
* :doc:`marc` MARC record manipulation including MARC record imports into traditional ILS
* `FUTURE` schema_org Schema.org microformat support
* :doc:`vendors` Contains vendor specific services
    * vendors.iii Innovative Patron API and item XML extraction applications
    * vendors.whitewhale White Whale design templates for Colorado College


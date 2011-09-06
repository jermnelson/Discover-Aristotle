:mod:`aristotle.etd` -- Electronic Thesis and Dissertation Django application
=============================================================================

Overview
^^^^^^^^
The Electronic Thesis and Dissertation Django application was originally a
pylons application developed at Colorado College. It has been migrated to the
Django and now is part of the Discover Aristotle bibliographic, repository,
and access framework being actively developed at Colorado College Tutt Library
and other institutions. Unless explictly set, all software code, ideas,
configuations, and any associated intellectual work is licensed under the Apache 2
open source license or under a Creative Commons copyright.


Dependencies
^^^^^^^^^^^^
The **etd** application requires the following modules from Emory University, EULFedora_
and EULXML_. If you want to support student datasets, you'll need into enable 
Aristotle's :doc:`datasets` application. If you want to supports MARC record generation 
from an object's MODS metadata, you will need to enable Aristotle's :doc:`marc`.

.. _EULFedora: https://github.com/emory-libraries/eulfedodra
.. _EULXML: https://github.com/emory-libraries/eulxml

`aristotle.etd.views` Module Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: etd.views
   :members:

`aristotle.etd.models` Supporting Models for ETD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: etd.models
   :members:

`aristotle.etd.tests` Unit tests for ETD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: etd.tests
   :members:


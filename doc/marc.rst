:mod:`aristotle.marc` MARC Records  Django Application
======================================================

Overview
^^^^^^^^
The **MARC Records Django Application** is a collection of
utilities for maninpulating MARC records. This application allows
for importing and exporting MARC records in an ILS, typically 
normalizing the various vendors MARC records to a single standard.

This application also allows MARC records to be generated out of
a Fedora digital repository for importing into an ILS or for external
authority control by such organizations as OCLC.

`aristotle.marc.views` Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.views
   :members:

`aristotle.marc.forms` Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.forms
   :members:

`aristotle.marc.models` Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.models
   :members:

`aristotle.marc.bots.marcbots` Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.marcbots
   :members:

Child MARC bots for specific publishers
=======================================

`aristotle.marc.bots.awbots` American West Bots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.awbots
   :members:

`aristotle.marc.bots.eccobots` Eighteenth Century Collections Online (ECCO)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.eccobots
   :members:

`aristotle.marc.bots.galebots` Gale Publishing files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.galebots
   :members:

`aristotle.marc.bots.gutenbergbots` Project Gutenberg
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.gutenbergbots
   :members:

`aristotle.marc.bots.ltibots` LTI Bots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.ltibots
   :members:

`aristotle.marc.bots.opbots` Oxford Press Bots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.opbots
   :members:

`aristotle.marc.bots.springerbots` Springer EBooks Bots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: marc.bots.springerbots
   :members:

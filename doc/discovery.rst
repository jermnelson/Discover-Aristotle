:mod:`aristotle.discovery` -- Aristotle Discovery Django application
=============================================================================

Overview
^^^^^^^^
The :mod:`aristotle.discovery` Django application started from a forked version of the 
Kochief_ Discovery interface and catalogue manager Django project. 

.. _Kochief: http://code.google.com/p/kochief/

Dependencies
^^^^^^^^^^^^
The **discovery** application doesn't have any external dependancies

Indexing MARC files
^^^^^^^^^^^^^^^^^^^
To index MARC records :mod:`aristotle.discovery` into the `marc_catalog`
Solr core, you will need to run the index management command from 
:mod:`aristotle` base directory.

`aristotle.discovery.views` Module Contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: discovery.views
   :members:

`aristotle.discovery.parsers.marc` MARC record Solr Import Parser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: discovery.parsers.marc
   :members:

`aristotle.discovery.parsers.tutt_maps` Location Maps for Tutt Library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: discovery.parsers.tutt_maps
   :members:

`aristotle.discovery.templatetags.discovery_extras` Template Tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: discovery.templatetags.discovery_extras
   :members:

`aristotle.discovery.management.commands.index` Management Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: discovery.management.commands.index
   :members:

:mod:`aristotle.vendors` -- Vendors Django Application
======================================================

Overview
^^^^^^^^
Aristotle isolates specific utilities and web services that interact
with various vendors into a sub-applications in a master Vendor Django
Application for a couple of reasons. The first is that allows common
functionality to be shared among different applications in the Aristotle
project. For example, the both the :doc:`catalog` and 
:doc:`etd` modules use the Innovative Patron API microservice to 
autenticate students for different uses. 


EBSCO Django Application
^^^^^^^^^^^^^^^^^^^^^^^^
**FUTURE FEATURE** Provides XML search interface for Ebsco Publishing's
full-text and citation databases 

III Django Application 
^^^^^^^^^^^^^^^^^^^^^^
A set of utilities for interacting with Innovative's Millennium ILS
includes Item status and Patron API interactions.

`vendors.iii.models` 
--------------------
.. automodule:: vendors.iii.models
   :members:

`vendors.iii.views` 
--------------------
.. automodule:: vendors.iii.views
   :members:


`vendors.iii.bots.iiibots`
--------------------------
.. automodule:: vendors.iii.bots.iiibots
   :members:


OCLC Django Application
^^^^^^^^^^^^^^^^^^^^^^^
**FUTURE FEATURE** Provides access to WorldCat and other OCLC web services
as well as FTP upload of MARC records for authority control.

White Whale Django Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Contains the design templates from White Whale for Colorado College's
discovery layer as well as a basic internal library website pages.

Templates
---------
* `templates/whitewhale/accessability.html` provides accessable navigation for web-page
* `templates/whitewhale/cc-collapsed-header.html` standard Collapsed header with main navigation for site
* `cc-footer.html` standard Colorado College footer

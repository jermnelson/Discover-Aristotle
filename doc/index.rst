.. Aristotle Documentation documentation master file, created by
   sphinx-quickstart on Wed Aug 24 08:57:57 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Aristotle Documentation |release|
============================================

Aristotle is a bibliographic Django_ project for creating discovery and management of born
digital and physical artifacts. Aristotle uses a number of other open-source toolset including
EULFedora_, EULXML_, Sunburnt_, and PyMARC_. For the Discovery interface, Aristotle uses a forked
version of the Kochief_ Django application. 

Project's documentation resides at `aristotle.readthedocs.org <http://aristotle.readthedocs.org/en/latest/>`_.

.. _Django: http://djangoproject.org/
.. _EULFedora: https://github.com/emory-libraries/eulfedodra
.. _EULXML: https://github.com/emory-libraries/eulxml
.. _Kochief: http://code.google.com/p/kochief/
.. _Sunburnt: https://github.com/tow/sunburnt
.. _PyMARC: https://github.com/edsu/pymarc

.. sidebar:: About `Bots` and Versions

   You may be wondering as you explore Aristotle's code-base
   and documentation by the use of **bots** classes.

   A few years ago I read Daniel Suarez's great first
   novel `Daemon <http://thedaemon.com/>`_ and then later watched
   his FORA.tv's video lecture 
   `Daemon: Bot-Mediated Reality <http://fora.tv/2008/08/08/Daniel_Suarez_Daemon_Bot-Mediated_Reality>`_
   
   His vision of **bots** inspired a new design pattern I've been
   using in my own code. The python-based **bots** in Aristotle's
   framework encapsulate data and behavior for one or more related tasks
   within a single class. I try to keep each `bot` class as simple and 
   framwork agnostic as possible so I use these **bots** logic in multiple
   places. This design pattern lends itself very well to programming
   `Micro-Services <http://www.ijdc.net/index.php/ijdc/article/view/154>`_.

   Aristotle uses `Semantic Versioning <http://semver.org/>`_ with the following
   format X.Y.Z or Major.Minor.Patch. We are currently targeting a full public stable
   API and production stable 1.0.0 by the forth quarter of 2011. 

Contents:

.. toctree::
   :maxdepth: 4

   readme.rst
   install.rst
   discovery.rst
   catalog.rst
   datasets.rst
   etd.rst
   grx.rst
   marc.rst
   vendors.rst
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


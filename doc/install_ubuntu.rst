Installing Aristotle on Ubuntu
==============================

Overview
^^^^^^^^
Directions for installing `Aristotle` on a Ubuntu_ 11.04 server running on virtual machine. 

.. _Ubuntu: http://www.ubuntu.com

Installing supporting software
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Before installing the remainder of the Python supporting modules, make sure you
have the Gnu C++ compiler installed. These packages were installed in the 
following order:

1. As super-user, install gcc with apt-get
   **$ sudo apt-get install gcc**
2. As super-user, install the dpkg-dev with apt-get
   **$ sudo apt-get install dpkg-dev**
3. As super-user, install curl
   **$ sudo apt-get install curl**
4. As super-user, install libxml2-dev
   **$ sudo apt-get install libxml2-dev**
5. As super-user, install memcached
   **$ sudo apt-get install memcached**
6. As super-user, install libxslt1-dev
   **$ sudo apt-get install libxslt1-dev**
7. As super-user, install python-dev
   **$ sudo apt-get install python2.7-dev**
8. As super-user, install python-flup
   **$ sudo apt-get install python-flup**

Installing Django
^^^^^^^^^^^^^^^^^
The Tutt Library uses the Python-based web framework called Django_. Please 
follow the steps listed below.

.. _Django: http://www.djangoproject.com/

1. Download stable version of Django (currently 1.3)
2. From the command-line decompress tar file:
   **$ tar xzvf Django-1.3.tar.gz**
3. Change directories to the Django-1.3
4. Install Django w/ super-user:
   **$ sudo python setup.py install**

Installing Aristotle Python Supporting Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Aristotle Django project for all the Tutt Library Python 
development requires the following Python modules for its functionality.  
Please download and install in this order of modules (some modules require some 
dependencies to be installed first)

distribute - `http://pypi.python.org/pypi/distribute <http://pypi.python.org/pypi/distribute>`_
-----------------------------------------------------------------------------------------------
1. Download the distribute installation script:
   **$ wget http://python-distribute.org/distribute_setup.py**
2. Install distribute w/super-user:
   **$ sudo python distribute_setup.py install**

pip - `http://www.pip-installer.org <http://www.pip-installer.org/>`_
---------------------------------------------------------------------------
1. Download the pip installer script:
   **$ curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py**
2. Install pip w/super-user
   **$ sudo python get-pip.py**

httplib2 - `http://code.google.com/p/httplib2/ <http://code.google.com/p/httplib2/>`_
-------------------------------------------------------------------------------------
1. Download the latest version of httplib2:
   **$ wget http://httplib2.googlecode.com/files/httplib2-0.7.1.tar.gz**
2. Extract the tar file:
   **$ tar -xf httplib2-0.7.1.tar.gz**
3. Go to the extracted directory:
   **$ cd httplib2-0.7.1**
4. Install httplib2 with super-user:
   **$ sudo python setup.py install**

lxml - `http://lxml.de/ <http://lxml.de/>`_
-------------------------------------------
1. Install lxml using pip w/super-user:
   **$ sudo pip install lxml**

sunburnt - `https://github.com/tow/sunburnt/ <https://github.com/tow/sunburnt/>`_
---------------------------------------------------------------------------------
1. Install sunburnt using pip w/super-user
   **$ sudo pip install sunburnt**

eulxml - `https://github.com/emory-libraries/eulxml <https://github.com/emory-libraries/eulxml>`_
-------------------------------------------------------------------------------------------------
1. Install eulxml using pip w/super-user
   **$ sudo pip install eulxml**

eulfedora - `https://github.com/emory-libraries/eulfedora <https://github.com/emory-libraries/eulfedora>`_
----------------------------------------------------------------------------------------------------------
1. Install eulxml using pip w/super-user
   **$ sudo pip install eulfedora**

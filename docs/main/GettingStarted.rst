===============
Getting Started
===============

:Status: Draft.

This guide will help quickly get you up and running with a local copy of
Moksha.  It will run the Moksha WSGI application using the Paste threaded http
server, a single orbited daemon with an embeded MorbidQ stomp message broker,
flat-file feed caches, SQLite SQLAlchemy databases, and an in-memory cache.
This setup is meant to be dead-simple to get up and running, and is not
designed for production deployments.

At the moment, all of Moksha's dependencies are not all in Fedora.  They are
all currently under review, but in the mean time you can run Moksha within a
virtual Python environment, without changing your global site-packages.

Setting up a Moksha virtualenv
------------------------------

.. code-block:: bash

    # yum install python-virtualenv

* Follow the TurboGears2 documentation for `Creating a virtual environment <http://turbogears.org/2.0/docs/main/DownloadInstall.html#create-a-virtual-environment>`_

Getting the Moksha source
-------------------------

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha 
    $ cd moksha
    $ python setup.py egg_info develop

Running Orbited
---------------

.. code-block:: bash

    $ orbited

Running Moksha
--------------

.. code-block:: bash

    $ paster serve development.ini

Using Moksha
------------

`http://localhost:8080 <http://localhost:8080>`_

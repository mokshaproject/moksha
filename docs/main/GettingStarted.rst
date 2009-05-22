===============
Getting Started
===============

:Status: Draft.

This guide will help quickly get you up and running with a local copy of
Moksha.  It will run the Moksha WSGI application using the Paste threaded http
server, a single orbited daemon with an embeded MorbidQ stomp message broker,
SQLite SQLAlchemy and Feed databases, and an in-memory cache.  This setup is
meant to be dead-simple to get up and running, and is not designed for
production deployments.

At the moment, all of Moksha's dependencies are not all in Fedora.  They are
all currently under review, but in the mean time these instructions will run
Moksha within a virtual Python environment, without changing your global
site-packages.

You can track the progress of getting TurboGears2 into Fedora `here <http://fedoraproject.org/wiki/TurboGears2>`_.

Installing the necessary dependencies
-------------------------------------

You'll need the `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ package.

.. code-block:: bash

    # yum -y install python-virtualenv python-memcached gcc

The `start-moksha` script mentioned below should install all of the necessary
dependencies.  However, it will attempt to compile a few things, such as lxml.  So, you may need to install some additional dependencies like `libxml2` and `libxslt` in order to build it.  If you're using yum, you can easily install all of the build requirements by doing:

.. code-block:: bash

    # yum-builddep -y python-lxml PyOpenSSL python-sqlite2

Getting the Moksha source
-------------------------

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha
    $ cd moksha

Starting Moksha
---------------

.. code-block:: bash

    $ ./start-moksha

.. note::
   Do not run this command as root.

.. note::
   This script takes care of setting up your TurboGears2 virtual environment
   the first time it is run.  To drop into the virtualenv manually you can run
   `source tg2env/bin/activate` to enter it, and `deactivate` to leave it.

Stopping Moksha
---------------

.. code-block:: bash

    $ ./stop-moksha

Using Moksha
------------

Now you can navigate your web browser to the following url:

`http://localhost:8080 <http://localhost:8080>`_

.. note::
   Going to `127.0.0.1` will not work properly with the current Orbited setup,
   so you must make sure to go to `localhost`.

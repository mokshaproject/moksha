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

    # yum -y install python-virtualenv
    # yum-builddep -y python-lxml
    $ easy_install -i http://www.turbogears.org/2.0/downloads/current/index tg.devtools

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

You will need to open a new tab to run Moksha, since Orbited will be using the original shell.  This will require you to activate your virtualenv again, by running `source tg2env/bin/activate`.

.. code-block:: bash

    $ paster serve development.ini

Running the Moksha Hub
----------------------

The Moksha Hub will eventually be a plugin-driven expert system that monitors
various data sources, allowing developers to implement hooks that take action
upon specific events.  It will handle polling feeds, API calls, etc -- and will
send messages to the AMQP message broker.

At the moment, however, this hub merely provides data to the default Moksha demo page.

.. code-block:: bash

    $ python moksha/hub.py

Using Moksha
------------

`http://localhost:8080 <http://localhost:8080>`_

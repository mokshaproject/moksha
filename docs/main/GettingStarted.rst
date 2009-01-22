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
    $ virtualenv --no-site-packages tg2env
    $ source tg2env/bin/activate
    $ easy_install -i http://www.turbogears.org/2.0/downloads/current/index tg.devtools

Getting the Moksha source
-------------------------

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha 
    $ cd moksha
    $ python setup.py egg_info develop

Installing the RabbitMQ AMQP message broker
-------------------------------------------

.. toctree::
   :maxdepth: 2

   RabbitMQ

Starting Moksha
---------------

.. code-block:: bash

    $ ./start-moksha


Stopping Moksha
---------------

.. code-block:: bash

    $ ./stop-moksha

Using Moksha
------------

Now you can navigate your web browser to the following url:

`http://localhost:8080 <http://localhost:8080>`_

:Note: Going to `127.0.0.1` will not work properly with the current Orbited setup, so you must make sure to go to `localhost`.

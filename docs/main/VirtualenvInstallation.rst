Virtualenv installation (Other Linux distros, OSX, Windows, etc)
----------------------------------------------------------------

This guide will help quickly get you up and running with a local copy of
Moksha.  It will run the Moksha WSGI application using the Paste threaded http
server, a single Orbited socket-proxy daemon with an embeded MorbidQ stomp message broker,
SQLite SQLAlchemy and Feed databases, and an in-memory cache.  This setup is
meant to be dead-simple to get up and running, and is not designed for
production deployments.

This installation method has been tested with OSX, Fedora, and RHEL.
See the :doc:`RPMInstallation` for a deploying with RPM and mod_wsgi.

Installing the necessary dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll need the `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ package.

For Fedora/Red Hat/CentOS based environments:

.. code-block:: bash

    # yum -y install python-virtualenv gcc openssl-devel zeromq-devel
    # yum-builddep -y python-lxml pyOpenSSL python-sqlite2

On Ubuntu/Debian:

.. code-block:: bash

   # apt-get install git python-dev python-virtualenv zeromq-dev

Install moksha
~~~~~~~~~~~~~~

.. code-block:: bash

    $ virtualenv myenv
    $ pip install moksha mdemos.server mdemos.menus mdemos.metrics

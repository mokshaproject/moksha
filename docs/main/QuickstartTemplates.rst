===========================
Moksha Quickstart Templates
===========================

Moksha provides templates for easily creating basic components.

.. code-block:: bash

   $ paster moksha --help
   Usage: /usr/bin/paster moksha [options]
   Create new Moksha components

   Options:
     --version             show program's version number and exit
     -h, --help            show this help message and exit
     -l, --livewidget      Create an example Moksha LiveWidget
     -c, --connector       Create an example Moksha Connector
     -u, --consumer        Create an example Moksha Consumer
     -C, --controller      Create an example Moksha Controller
     -P, --producer Create an example Moksha Producer
     -p PACKAGE, --package=PACKAGE
                           package name for the code
     -t TOPIC, --topic=TOPIC
                           The Moksha topic to utilize

.. note::

   All of the above options can be mixed/matched and used to generate a
   plugin with different components.


Creating a new moksha app with all components
---------------------------------------------

.. code-block:: bash

   $ paster moksha --livewidget --producer --consumer --controller


Creating and installing an RPM for your new package
---------------------------------------------------

.. code-block:: bash

   $ paver reinstall


Creating a new TurboGears2 app
------------------------------

See the `TurboGears2 QuickStart Documentation <http://turbogears.org/2.0/docs/main/QuickStart.html>`_ as well as the :doc:`IntegratingWithTG2` example.


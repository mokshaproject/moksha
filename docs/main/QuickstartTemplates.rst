===========================
Moksha Quickstart Templates
===========================

Moksha provides templates for easily creating basic widgets, streams,
consumers, etc.

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
     -s, --stream          Create an example Moksha DataStream
     -p PACKAGE, --package=PACKAGE
                           package name for the code
     -t TOPIC, --topic=TOPIC
                           The Moksha topic to utilize
     --dry-run             dry run (don't actually do anything)
     --noinput             no input (don't ask any questions)

.. note::

   All of the above options can be mixed/matched and used to generate a
   plugin with different components.


Creating a new moksha app with all components
---------------------------------------------

.. code-block:: bash

   $ paster moksha --livewidget --stream --consumer --controller


Creating and installing an RPM for your new package
---------------------------------------------------

.. code-block:: bash

   $ paver reinstall


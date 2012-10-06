===========================
Moksha Quickstart Templates
===========================

If you're a TurboGears2 user, you're in luck!
Moksha provides templates for easily creating basic components.

.. code-block:: bash

   $ paster moksha --help
   Usage: /usr/bin/paster moksha [options]
   Create new Moksha components

   Options:
     --version             show program's version number and exit
     -h, --help            show this help message and exit
     -l, --livewidget      Create an example Moksha LiveWidget
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

Quick and dirty method of running your app
------------------------------------------

This command will run the entire Moksha stack, including orbited, paster WSGI
server, and the moksha-hub, along with your application.

.. code-block:: bash

   $ moksha start

Creating and installing an RPM for your new package
---------------------------------------------------

.. code-block:: bash

   $ paver reinstall


Creating a whole new app
------------------------

See:

 - :doc:`tutorials/TurboGears2`
 - :doc:`tutorials/Pyramid`
 - :doc:`tutorials/Flask`

===================
Hacking with Moksha
===================

Getting the code
----------------

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha

Rebuilding and Reinstalling the RPM
-----------------------------------

.. code-block:: bash

    $ paver reinstall

Reinstalling *all* apps
-----------------------

.. code-block:: bash

    $ paver reinstall_apps


Reinstall everything, and restart apache
----------------------------------------

.. code-block:: bash

    $ paver reinstall reinstall_apps restart_httpd

.. note::

   These instructions assume that you already have an RPM development
   environment setup.  To do this, simply install `rpmdevtools` and run
   `rpmdev-setuptree`

.. note::

   The instructions below are considered to be deprecated.
   The ideal installation mechanism is via RPM.

Starting
--------

.. code-block:: bash

    $ ./start-moksha

Stopping
--------

.. code-block:: bash

    $ ./stop-moksha


Generating documentation
------------------------

.. code-block:: bash

    $ paver html

Running the test suite
----------------------

.. code-block:: bash

    $ nosetests

Freezing requirements
---------------------

.. code-block:: bash

    $ ./pip.py freeze -E tg2env -r normal-reqs.txt production/stable-reqs.txt

Profiling the WSGI stack
------------------------

Open the :file:`moksha/config/app_cfg.py` file and set the `base_config.profile` variable to `True`.  After surfing around your application, you can then go to `http://localhost:8080/__profile__ <http://localhost:8080/__profile__>`_ to view your profiling statistics.

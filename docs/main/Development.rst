===================
Hacking with Moksha
===================

Setting up your RPM/virtualenv development environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:RPM mod_wsgi installation (Red Hat, Fedora, etc.): :doc:`RPMInstallation`
:virtualenv installation (OSX, Ubuntu, etc.): :doc:`VirtualenvInstallation`

Getting the code
~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha

Rebuilding and reinstall *everything*, and restart apache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver reinstall reinstall_apps restart_httpd

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver html

Running the test suite
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ nosetests

Freezing requirements
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ pip freeze -E tg2env -r requirements.txt production/stable-reqs.txt

Profiling the WSGI stack
------------------------

Open the :file:`moksha/config/app_cfg.py` file and set the `base_config.profile` variable to `True`.  After surfing around your application, you can then go to `http://localhost:8080/__profile__ <http://localhost:8080/__profile__>`_ to view your profiling statistics.

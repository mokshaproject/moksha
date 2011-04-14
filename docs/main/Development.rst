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


Rebuilding and reinstalling Moksha
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver reinstall

Rebuilding and reinstalling all Moksha apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver reinstall_apps

Rebuilding and reinstalling a specific Moksha apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver reinstall_app --app=metrics

Restart apache and load the front page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver restart_httpd


Restart the Moksha Hub
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver restart_hub


Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver html

Running the test suite
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver test

Rebuilding and reinstall *everything*, restart apache, and run the test suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ paver reinstall reinstall_apps restart_httpd restart_hub test

.. note::

   As a developer, performing the full rebuild, reinstall, restart, and test
   sequence is usually a good habit to get into, however it can take a long
   time.  If you're hardcore, this `RPM patch <http://www.rpm.org/ticket/92>`_
   will speed things up quite a bit.

Freezing requirements
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ pip freeze -E ~/.virtualenvs/moksha -r requirements.txt production/stable-reqs.txt

Profiling the WSGI stack
------------------------

Open the :file:`moksha/config/app_cfg.py` file and set the `base_config.profile` variable to `True`.  After surfing around your application, you can then go to `http://localhost:8080/__profile__ <http://localhost:8080/__profile__>`_ to view your profiling statistics.

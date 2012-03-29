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
    $ cd moksha/

Bootstrapping Your Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ ./moksha-ctl.py bootstrap

Rebuilding and reinstalling Moksha
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py rebuild

Rebuilding and reinstalling all Moksha apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ workon moksha
   (moksha) $ pip install --upgrade mdemos.all
   (moksha) $ deactivate

Rebuilding and reinstalling a specific Moksha apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ workon moksha
   (moksha) $ pip install --upgrade mdemos.metrics
   (moksha) $ deactivate

Restart paster
~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py restart:paster

Restart the Moksha Hub
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py restart:moksha-hub

Debugging your setup
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py wtf

Watching the logs
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py logs

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver html

Running the test suite
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ workon moksha
    (moksha) $ python setup.py test
    (moksha) $ deactivate

Rebuilding and reinstall *everything*, restart *everything*, and run the test suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ ./moksha-ctl.py rebuild restart
   $ workon moksha
   (moksha) $ python setup.py test
   (moksha) $ deactivate

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

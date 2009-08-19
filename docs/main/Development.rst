===================
Hacking with Moksha
===================

RPM Installation
----------------

Install the dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

Run the following commands as root, replacing `$DISTRO` with either
`fedora-11`, `fedora-10`, or `epel-5`.

.. code-block:: bash

   # cd /etc/yum.repos.d/
   # wget http://lmacken.fedorapeople.org/rpms/tg2/$DISTRO/tg2.repo
   # yum -y install TurboGears2 python-tg-devtools

.. note::

   It is recommended that you perform a `yum update` after installing the
   Moksha/TurboGears2 stack, to ensure that you have the latest versions
   of all the dependencies.

.. note::

   At the moment the full TurboGears2 stack is not yet fully in Fedora/EPEL, 
   so you'll have to hook up a third party repository.  You can track the
   status of TurboGears2 in Fedora here:

   http://fedoraproject.org/wiki/TurboGears2

Getting the code
~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha

Rebuilding and Reinstalling the RPM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver reinstall

Reinstalling *all* apps
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver reinstall_apps


Reinstall everything, and restart apache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ paver reinstall reinstall_apps restart_httpd

.. note::

   These instructions assume that you already have an RPM development
   environment setup.  To do this, simply install `rpmdevtools` and run
   `rpmdev-setuptree`



Non-RPM installation (OSX)
--------------------------

This installation method should work on non

Getting the code
~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha

Starting
~~~~~~~~

.. code-block:: bash

    $ ./start-moksha

Stopping
--------

.. code-block:: bash

    $ ./stop-moksha


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

    $ ./pip.py freeze -E tg2env -r normal-reqs.txt production/stable-reqs.txt

Profiling the WSGI stack
------------------------

Open the :file:`moksha/config/app_cfg.py` file and set the `base_config.profile` variable to `True`.  After surfing around your application, you can then go to `http://localhost:8080/__profile__ <http://localhost:8080/__profile__>`_ to view your profiling statistics.

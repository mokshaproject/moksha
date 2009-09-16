==============================================
Setting up a Moksha RPM & mod_wsgi environment
==============================================

Setup the TurboGears2/Moksha yum repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the moment, all of Moksha's dependencies are not all in Fedora.  They are
all currently under review, but in the mean time these instructions will run
Moksha within a virtual Python environment, without changing your global
site-packages.

You can track the progress of getting TurboGears2 into Fedora `here <http://fedoraproject.org/wiki/TurboGears2>`_.

To setup Luke Macken's TurboGears2 yum repository, run the following commands
as root, replacing `$DISTRO` with either `fedora-rawhide`, `fedora-11`,
`fedora-10`, or `epel-5`.

.. code-block:: bash

   cd /etc/yum.repos.d/
   curl -O http://lmacken.fedorapeople.org/rpms/tg2/$DISTRO/tg2.repo
   yum -y install TurboGears2 python-tg-devtools

.. note::

   It is recommended that you perform a `yum update` after installing
   the Moksha/TurboGears2 stack, to ensure that you have the latest
   versions of all the dependencies.

.. note::

   At the moment the full TurboGears2 stack is not yet fully in
   Fedora/EPEL, so you'll have to hook up a third party repository.  You
   can track the status of TurboGears2 in Fedora here:

   http://fedoraproject.org/wiki/TurboGears2

Install the dependencies and setup your RPM tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo yum install rpmdevtools python-paver python-tg-devtools TurboGears2
   $ sudo yum-builddep -y moksha
   $ rpmdev-setuptree

Installing the Moksha Apache/mod_wsgi server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo yum install moksha-{server,hub,docs}


Running Moksha
~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo /sbin/service httpd restart


Running Orbited
~~~~~~~~~~~~~~~

.. code-block:: bash

   $ orbited


Running the Moksha Hub
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo /sbin/service moksha-hub restart


Watching the Error Log
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo tail -f /var/log/httpd/moksha_error_log

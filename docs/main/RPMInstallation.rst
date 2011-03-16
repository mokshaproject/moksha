=====================================================================
Setting up a Moksha RPM & mod_wsgi environment (Fedora, RHEL, CentOS)
=====================================================================

Installing the Moksha Apache/mod_wsgi server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo yum install moksha-{server,hub,docs}

.. note::

   The above setup does not install any apps.  To duplicate the moksha
   dashboard demo, you can `yum install moksha\*`

Running Moksha
~~~~~~~~~~~~~~

.. code-block:: bash

   $ sudo /sbin/service httpd restart


Running Orbited
~~~~~~~~~~~~~~~

Out of the box Orbited comes with a very minimal configuration

Copy over Moksha's Orbited configuration:

.. code-block:: bash

   # cp /etc/moksha/orbited.cfg /etc/orbited.cfg

.. note::

   Moksha's Orbited configuration enables the MorbidQ STOMP message broker by default,
   for ease of development.  This can be disabled by commenting out the line ``stomp://:61613``
   and the line under the ``[access]`` section.

Starting the Orbited daemon

.. code-block:: bash

   # service orbited start

.. note::

   You can also start orbited by hand by running ``orbited -c /etc/moksha/orbited.cfg``


Running the Moksha Hub
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # service moksha-hub start


Install the dependencies and setup your RPM tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is only necessary if you plan on building moksha apps.

.. code-block:: bash

   $ sudo yum install rpmdevtools
   $ rpmdev-setuptree
   $ sudo yum-builddep -y moksha


Watching the logs
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # tail -f /var/log/httpd/moksha_{access,error}_log
   # tail -f /var/log/moksha/moksha-hub.log

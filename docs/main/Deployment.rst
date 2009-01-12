==========
Deployment
==========

:Status: Incomplete

Installing and configuring Moksha
---------------------------------

TODO

Setting up mod_wsgi
-------------------

TODO

Setting up orbited
------------------

TODO

Choosing a message broker
-------------------------

By default Moksha utilizes the embeded MorbidQ message broker inside of Orbited.  This allows for widgets to communicate with the server using the Stomp protocol.  In production you can easily switch to an enterprise-grade message broker, such as RabbitMQ, and [eventually] Qpid.

.. toctree::
   :maxdepth: 2

   RabbitMQ


Using Qpid with MokshA
~~~~~~~~~~~~~~~~~~~~~~

:Status: Coming soon

Setting up memcached
--------------------

TODO

Setting up the database
-----------------------

TODO


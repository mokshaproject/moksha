===============
Message Brokers
===============

Moksha supports configurable message flows, allowing you to utilize various
message brokers, depending on your environment.

Since Moksha employs a high-level `"Topic"` concept, applications can easily
communicate with them without having to worry about the underlying message
protocol.

`STOMP <http://stomp.codehaus.org/Protocol>`_
---------------------------------------------

By default, Moksha will utilize the `STOMP
<http://stomp.codehaus.org/Protocol>`_ message broker, `MorbidQ
<www.morbidq.com>`_, which is built-in to `Orbited <http://orbited.org>`_.  You
can change the `stomp_broker` in the Moksha configuration file to point to a
different STOMP broker -- `RabbitMQ <http://rabbitmq.com>`_ with the STOMP-adapter has been tested as
well.

`AMQP <http://amqp.org>`_
-------------------------

Plugging an `AMQP <http://amqp.org>`_ broker into Moksha is trivial.  Simply
add an `amqp_broker` to your configuration, and change the live socket backend:

.. code-block:: none

    amqp_broker = guest/guest@localhost
    moksha.livesocket.backend = amqp

.. note::

   It's probably best to comment out the `stomp_broker` when you enable AMQP
   support.  You can have both, but Moksha will enter a bridged mode that
   may or may not work as expected.

The :class:`MokshaHub` will then automatically connect up to your AMQP broker and proxy messages to the STOMP broker and Moksha Consumers.

AMQP support in Moksha has been tested with `Qpid <http://qpid.apache.org>`_.

`RabbitMQ <http://rabbitmq.com>`_ support is under development.  See the :doc:`RabbitMQ` documentation for details on testing it.

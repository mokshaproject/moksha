==========================
Using RabbitMQ with Moksha
==========================

Moksha is currently being tested with the RabbitMQ AMQP message broker.
Eventually, it should be able to work out of the box with any AMQP broker out
there, but for now we need RabbitMQ because it has STOMP bindings.  Since the
AMQP javascript bindings are currently under development, our widgets have to
speak in the STOMP protocol to the broker, through Orbited.



Install and run RabbitMQ
------------------------

Moksha comes with a simple `run` script that should take care of everything for
you.

.. code-block:: bash

    # yum -y install erlang{,-esdl}
    $ cd rabbitmq
    $ ./run


Configure Moksha to use RabbitMQ.
---------------------------------

Edit Moksha's `orbited.cfg` and comment out the `stomp` listener.

.. code-block:: none

    # This enables Orbited's built-in MorbidQ message queue.
    # Comment this out if to use your own, eg: RabbitMQ
    #stomp://:61613

Then, edit Moksha's `development.ini` to point to your RabbitMQ broker.

.. code-block:: none

    [DEFAULT]
    stomp_host = localhost
    stomp_port = 61613
    stomp_user = guest
    stomp_pass = guest


Production modifications
------------------------

Change the password of the guest account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: none

        rabbitmqctl change_password username newpassword

    Then open Moksha's `development.ini` and set the `stomp_user` and
    `stomp_pass` to your newly set credentials.

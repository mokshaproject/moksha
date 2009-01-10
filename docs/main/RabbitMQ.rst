==========================
Using RabbitMQ with Moksha
==========================

:Status: Hacked together.
:Todo: Package RabbitMQ, so it can be properly installed and run.

Install RabbitMQ
------------------

.. code-block:: none

    http://www.rabbitmq.com/install.html

Change the password of the guest account
----------------------------------------

.. code-block:: none

    rabbitmqctl change_password username newpassword

Then open Moksha's `development.ini` and set the `stomp_user` and
`stomp_pass` to your newly set credentials.

Grab the rabbitmq-stomp adapter
-------------------------------

.. code-block:: none

    hg clone http://hg.rabbitmq.com/rabbitmq-stomp

Running RabbitMQ with the stomp adapter
---------------------------------------

.. code-block:: none

    cd rabbitmq-stomp
    make start_server


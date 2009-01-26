================
Data Aggregation
================

Moksha provides many ways to acquire data in an efficient manner.

Messaging layer
---------------

Moksha can communicate with various message brokers, using the `AMQP <http://amqp.org>`_ and/or `STOMP <http://stomp.codehaus.org/Protocol>`_ protocols.  It also provides a simple API for sending and consuming messages, as well as allowing widgets to subscribe to live messages streams within the users web browser.

Caching layer
-------------

A flexible caching layer is available to all Moksha widgets and applications.
This middleware is setup by TurboGears2, and trivializes the act of caching
expensive operations.

Resource layer
--------------

Moksha provides an API for interacting with other API's.  A developer is able
to easily create or utilize connectors for existing external resources and
services.

Moksha Feed API
---------------

Moksha provides a powerful Feed widget that automatically handles fetching,
parsing, and caching arbitrary feeds in an efficient, scalable manner.

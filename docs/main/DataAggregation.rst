================
Data Aggregation
================

Moksha provides many ways to acquire data in an efficient manner.

Caching layer
-------------

A simple caching layer is available to all Moksha widgets and applications that
trivializes the act of caching expensive operations.  The cache layer is very
flexible, and can scale with your architecture.  For example, you could start
with a simple in-memory cache for development, and transparently deploy to a
cloud of memcached servers in a production environment.

Resource layer
--------------

Moksha provides an API for interacting with other API's.  A developer is able
to create or utilize clients for existing external services.  Moksha handles
setting up and maintaining these client sessions, making them available across
all Moksha widgets/applications, as well as making it simple to cache arbitrary
resource queries.

Since Moksha can be made aware of existing resources, it could also potentially
handle spidering and indexing those resources, and provide a powerful search
engine.

Moksha Feed API
---------------

Moksha provides a powerful Feed widget that automatically handles fetching,
parsing, and caching arbitrary feeds in an efficient, scalable manner.

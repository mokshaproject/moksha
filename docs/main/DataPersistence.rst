================
Data Persistence
================

Moksha is designed to wield dynamic data from arbitrary resources.  It also
provides a variety of ways to enable data persistence.

SQLAlchemy
----------

The :class:`moksha.middleware.MokshaMiddleware` automatically handles setting up the database engines and initializing tables for all application models.  This gives Moksha the ability to properly handle vertically and horizontally scaling application databases.

Cache
-----

Moksha gives every application and widget the ability to use a generic Cache
object to store and retrieve arbitrary data, allowing developers to design
efficient applications from the start.  This Cache object is setup by
Moksha, and can easily be configured to work with any number of arbitrary data
stores, such as memcached, Amazon S3, SQLite, etc.

Git
---

Moksha will also make it simple to define data sources that should persist in a
git repository.  This allows developers to easily track, interpret, and
reference revisions of arbitrary data sources.

RHM
---

`RHM <http://rhm.et.redhat.com>`_ is a persistence extension to the Qpid
messaging system.  Since Moksha integrates with the Qpid AMQP messaging broker,
the RHM extension will give Moksha applications the ability to define
persistent durable messages queues.

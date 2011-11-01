================
Data Persistence
================

Moksha is designed to wield dynamic data from arbitrary resources.  It also
provides a variety of ways to enable data persistence.

`SQLAlchemy <http://sqlalchemy.org>`_
-------------------------------------

The :class:`moksha.middleware.MokshaMiddleware` automatically handles setting
up the SQLAlchemy database engines and initializing tables for all application
models.

Cache
-----

Every application and widget has the ability to use a powerful cache module to
store and retrieve arbitrary data, allowing developers to design efficient
applications from the start.  This Cache layer is setup by TG2, and can
easily be configured to work with any number of arbitrary data stores, such as
an in-memory cache, SQLite, memcached, Amazon S3, etc.

Git
---

Although it does not yet, Moksha will also make it simple to define data
sources that should persist in a
git repository.  This allows developers to easily track, interpret, and
reference revisions of arbitrary data sources.

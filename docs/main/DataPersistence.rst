================
Data Persistence
================

Moksha is designed to wield dynamic data from arbitrary resources.  However, it
is intended to be "backend agnostic" when it comes to data persistence.

When configured, the :class:`moksha.wsgi.middleware.MokshaMiddleware`
can automatically handle setting up SQLAlchemy database engines and
initializing tables for all application models.

You can conceivably enable any storage backend from memcached, to zodb, to git.

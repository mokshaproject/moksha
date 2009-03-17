Security
========

Cross-site Request Forgery Protection
-------------------------------------

Moksha offers CSRF protection for authenticated users by default.
For more information on `CSRF`, see the `Wikipedia entry
<http://en.wikipedia.org/wiki/Cross-site_request_forgery>`_

WSGI Middleware
~~~~~~~~~~~~~~~

.. autoclass:: moksha.middleware.csrf.CSRFProtectionMiddleware
   :members: __call__

:mod:`repoze.who` metadata provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: moksha.middleware.csrf.CSRFMetadataProvider
   :members: add_metadata

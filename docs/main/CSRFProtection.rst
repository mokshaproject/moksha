Security
========

Cross-site Request Forgery Protection
-------------------------------------

Moksha offers a layer of CSRF protection for authenticated users.
For more information on `CSRF`, see the `Wikipedia entry
<http://en.wikipedia.org/wiki/Cross-site_request_forgery>`_

You can enable/disable this middleware by using the following configuration
option in your ``production.ini`` file:

.. code-block:: python

   moksha.csrf_protection = True

WSGI Middleware
~~~~~~~~~~~~~~~

.. autoclass:: moksha.middleware.csrf.CSRFProtectionMiddleware
   :members: __call__

:mod:`repoze.who` metadata provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: moksha.middleware.csrf.CSRFMetadataProvider
   :members: add_metadata

Moksha Middleware
=================

Moksha can run as an application serving platform on its own, but
also contains a small piece of WSGI middleware that provides your 
application with a lot of additional functionality as well.  This allows you to use Moksha in your existing `WSGI <http://www.python.org/dev/peps/pep-0333/>`_ application.

It currently provides the following functionality

    * Sets up the feed storage and cache for widgets
    * Handles dispatching moksha applications, which can be any WSGI app
    * Handles dispatching to individual widgets, which are simply `ToscaWidgets <http://toscawidgets.org>`_
    * Sets up `SQLAlchemy` database engines for each application
    * Initializes applications data models
    * Loads all application configuration

Using the MokshaMiddleware
--------------------------

Using the MokshaMiddleware with an existing WSGI application is quite
simple.  It will look a bit different with each framework, but here is
how it looks in TurboGears2.

.. code-block:: python

    """TurboGears middleware initialization"""
    from myapp.config.app_cfg import base_config
    from myapp.config.environment import load_environment

    # make_base_app will wrap the TG2 app with all the middleware it needs. 
    make_base_app = base_config.setup_tg_wsgi_app(load_environment)

    def make_app(global_conf, full_stack=True, **app_conf):
        from moksha.middlware import MokshaMiddleware
        app = make_base_app(global_conf, wrap_app=MokshaMiddleware,
                            full_stack, **app_conf)
        return app

:Note: It currently requires to be wrapped in the `paste.registry <http://pythonpaste.org/modules/registry.html>`_ WSGI middleware.  TurboGears2 allows us to easily insert middleware directly on top of the raw application, so we then have the ability to use the paste.registry, sessions, and caching.

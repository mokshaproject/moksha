Moksha Applications
===================

When the :class:`moksha.middleware.MokshaMiddleware` is loaded, it will
automatically load all applications and widgets from those entry points,
and store them in ``moksha.apps`` and ``moksha._widgets`` dictionaries.
These can then be accessed at any time by any application or widget during
any request.

Mounting an existing WSGI application
-------------------------------------

You can mount an existing WSGI application by pointing to it
in the ``setup.py`` on the ``[moksha.wsgiapp]`` entry-point.

.. code-block:: python

    [moksha.wsgiapp]
    mywsgiapp = mywsgiapp.wsgiapp:MyWSGIApplication

Your WSGI application will then be accessable via ``/appz/mywsgiapp`` in Moksha.

Using an existing TurboGears application
-------------------------------------------

You can easily mount TurboGears Controllers within Moksha by pointing to them in
your ``setup.py`` under the ``[moksha.application]`` entry-point.

.. code-block:: python

    [moksha.application]
    myapp = myapplication.controllers.root:RootController

Installing a ToscaWidget
------------------------

You can plug an existing ToscaWidget into Moksha by adding it to the ``[moksha.widget]`` entry-point.

.. code-block:: python

    [moksha.widget]
    jquery = tw.jquery:jquery_js

Configuration
-------------

Moksha will reads every application's ``production.ini`` or ``development.ini``
upon startup and loads all of the ``[DEFAULT]`` variables into the global
:class:`pylons.config` object.  This enables TG2/Pylons Moksha applications to
use the config object as they would do normally.  However, this requires that
applications do not have conflicting configuration variable names.  Moksha will
display a warning message for each variable conflict.  Resolving these can be
done by namespacing your configuration variables.  For example, if your config
variable is `foo=bar`, you could rename it to `myapp.foo=bar`.

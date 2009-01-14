Moksha Applications
===================

Creating a moksha application is a as easy as creating a new ToscaWidget or
TurboGears2/Pylons project.

Moksha entry points
-------------------

Moksha loads all applications and widgets from the ``moksha.application`` and
``moksha.widget`` setuptools entry point.  This allows for dynamic discovery
of moksha applications just by pointing to your WSGI Controller, or ToscaWidget
in your project's setup.py.

Here is an example of a bare-bones setup.py, and how to integrate it with
Moksha.

.. code-block:: python

    from setuptools import setup, find_packages

    setup(
        name='myproject',
        entry_points="""

        [moksha.widget]
        mywidget = myproject.mywidgets:MyWidget

        [moksha.application]
        myapp = myproject.controllers.root:BaseController

        """
    )


When the :class:`moksha.middleware.MokshaMiddleware` is loaded, it will
automatically load all applications and widgets from those entry points,
and store them in ``moksha.apps`` and ``moksha._widgets`` dictionaries.
These can then be accessed at any time by any application or widget during
any request.

Writing applications and widgets using TurboGears2
--------------------------------------------------

.. toctree::
   :maxdepth: 1

   tg2/docs/index


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

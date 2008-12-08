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
and store them in ``moksha.apps`` and ``moksha.widgets`` dictionaries.
These can then be accessed at any time by any application or widget during
any request.

Writing applications and widgets
--------------------------------

.. toctree::
   :maxdepth: 1

   tg2/docs/index

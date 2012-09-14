Moksha Plugin Entry Points
==========================

When the :class:`moksha.wsgi.middleware.MokshaMiddleware` is loaded, it will
automatically load all applications and widgets from those entry points,
and store them in ``moksha.common.utils.apps`` and
``moksha.common.utils._widgets`` dictionaries.  These can then be accessed
at any time by any application or widget during any request.

What is an Entry Point?
-----------------------

Entry points are a Python setuptools/distribute feature that allows packages to
register something under a specific key that other packages can query for.
This is how you make Moksha aware of your widgets/apps/producers/consumers.

Entry points are defined in your projects ``setup.py`` like so:

.. code-block:: python

   setup(name='moksha.helloworld',
         ...
         entry_points="""
            [moksha.widget]
            hellowidget = helloworld.widgets:HelloWorldWidget
         """

Mounting the root controller of your application
------------------------------------------------

Moksha allows you to easily configure the root controller of your application.
You can do this by mounting your controller on the ``[moksha.root]``
entry-point as ``root``, like so:

.. code-block:: python

    [moksha.root]
    root = myproject.controllers.root:RootController

.. seealso::

   `Writing TurboGears Controllers <http://turbogears.org/2.1/docs/main/Controllers.html>`_

Mounting a TurboGears application
----------------------------------

You can easily mount TurboGears Controllers within Moksha by pointing to them in
your ``setup.py`` under the ``[moksha.application]`` entry-point.

.. code-block:: python

    [moksha.application]
    myapp = myapplication.controllers.root:RootController

Your TG application will then be accessable via ``/apps/myapp`` in Moksha.
Moksha will also look for a ``model`` module in your application, and will call
the ``init_model`` method within it, if it exists.  This is a convention used to
initialize TurboGears2 models.

Installing a ToscaWidget
------------------------

You can plug an existing ToscaWidget into Moksha by adding it to the ``[moksha.widget]`` entry-point.

.. code-block:: python

    [moksha.widget]
    jquery = tw.jquery:jquery_js

Your Widget will then be accessable via ``/widgets/mywidget`` in Moksha.

Mounting a WSGI application
---------------------------

You can mount an existing WSGI application by pointing to it
in the ``setup.py`` on the ``[moksha.wsgiapp]`` entry-point.

.. code-block:: python

    [moksha.wsgiapp]
    mywsgiapp = mywsgiapp.wsgiapp:MyWSGIApplication

Your WSGI application will then be accessable via ``/apps/mywsgiapp`` in Moksha.

.. warning::

   At the moment it is not recommened that you mount a TurboGears/Pylons app as
   a WSGI application inside of Moksha, since the ``pylons.config`` objects
   will conflict.  This issue will be addressed in the future.  Instead, you can
   simply mount a Controller as a ``moksha.application``.

Configuration
-------------

Moksha will reads every application's ``production.ini`` or ``development.ini``
from ``/etc/moksha/conf.d/$APPNAME/`` upon startup and loads all of the ``[DEFAULT]`` variables into the global
:class:`pylons.config` object.  This enables TG2/Pylons Moksha applications to
use the config object as they would do normally.  However, this requires that
applications do not have conflicting configuration variable names.  Moksha will
display a warning message for each variable conflict.  Resolving these can be
done by namespacing your configuration variables.  For example, if your config
variable is `foo=bar`, you could rename it to `myapp.foo=bar`.


.. seealso::

   :doc:`GettingStarted` for details on getting things up and running,
   :doc:`QuickstartTemplates` for creating new Moksha Components, and
   :doc:`tutorials/TurboGears2` for using Moksha with TurboGears2.
   :doc:`tutorials/Pyramid` for using Moksha with Pyramid.
   :doc:`tutorials/Flask` for using Moksha with Flask.

=======
Caching
=======

TurboGears2 automatically sets up the `Beaker <http://beaker.groovie.org>`_
cache and session middleware, which can be freely used within any Moksha
application or widget.

Using the cache within a widget
-------------------------------

As mentioned in :doc:`Widgets`, Moksha supports both ToscaWidgets1 and
ToscaWidgets2 which have slightly different syntaxes.

For ToscaWidgets1:

.. code-block:: python

    from tw.api import Widget
    from pylons import cache

    class MyWidget(Widget):
        params = ['entries']
        template = """
          <ul>
            % for entry in entries:
                <li>${entry}</li>
            % endfor
          </ul>
        """
        engine_name = 'mako'

        def update_params(self, d):
            super(MyWidget, self).update_params(d)
            c = cache.get_cache('mywidget')
            d['entries'] = c.get_value(key='entries',
                                       createfunc=self.get_entries,
                                       expiretime=3600)

        def get_entries(self):
            """ Expensive operation goes here... """

For ToscaWidgets2:

.. code-block:: python

    from tw2.core import Widget, Param
    from pylons import cache

    class MyWidget(Widget):
        entries = Param("Some entries.", default=[])
        template = """
          <ul>
            % for entry in entries:
                <li>${entry}</li>
            % endfor
          </ul>
        """

        def prepare(self):
            super(MyWidget, self).prepare()
            c = cache.get_cache('mywidget')
            self.entries = c.get_value(key='entries',
                                       createfunc=self.get_entries,
                                       expiretime=3600)

        def get_entries(self):
            """ Expensive operation goes here... """

Changing the backend cache storage
----------------------------------

By default the cache middleware will use an in-memory cache.  Beaker has many `configuration options <http://wiki.pylonshq.com/display/beaker/Configuration+Options>`_ that allow for a variety of backend cache stores, such as "dbm", "file", "memcached", "database", and "memory".

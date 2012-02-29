The Moksha Feed Widget
----------------------

.. autoclass:: moksha.api.widgets.feed.Feed
   :members:

.. widgetbrowser:: moksha.widgets.demos.FeedDemo
   :tabs: demo, source, template
   :size: large

Using the Feed widget
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from moksha.api.widgets.feed import Feed
    feed = Feed('myfeed')
    feed(url='http://lewk.org/rss')

Rendering a url with the Feed object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    feed = Feed('myfeed')
    feed(url='http://lewk.org/rss')

.. note::
   Usually you would instantiate a single Feed object somewhere in your
   project, and just call it with a `url` when rendering it in your templates.

Subclassing
~~~~~~~~~~~

.. code-block:: python

    class MyFeed(Feed):
        url = 'http://foo.com/feed.xml'

    myfeed = MyFeed()
    myfeed() # renders the widget, usually done in the template

As ToscaWidget children
~~~~~~~~~~~~~~~~~~~~~~~

By defining your Feeds as children to a widget, ToscaWidgets1 will automatically
handle setting a unique id for your Feed object, as well as giving you the
ability access it in your template from the `c` context object.

.. code-block:: python

    from tw.api import Widget
    from moksha.api.widgets.feed import Feed

    class MyWidget(Widget):
        myfeedurl = 'http://foo.com/feed.xml'
        children = [Feed('myfeed', url=myfeedurl)]
        template = "${c.myfeed()}"

The usage for ToscaWidgets2 is quite similar.

.. code-block:: python

    from tw2.core import Widget
    from moksha.api.widgets.feed import Feed

    class MyWidget(Widget):
        myfeedurl = 'http://foo.com/feed.xml'
        myfeed = Feed(url=myfeedurl)
        template = "${w.myfeed()}"

As a generator
~~~~~~~~~~~~~~

For ToscaWidgets1:

.. code-block:: python

    feed = Feed('myfeed', url='http://foo.com/feed.xml')
    print '%d entries' % feed.num_entries()
    for entry in feed.iterentries():
        print entry.title

For ToscaWidgets2:

.. code-block:: python

    feed = Feed(id='myfeed', url='http://foo.com/feed.xml')
    print '%d entries' % feed.num_entries()
    for entry in feed.iterentries():
        print entry.title

Using the moksha feed cache by hand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The moksha Feed widget automatically handles fetching and caching your feeds
using the global moksha feed cache.  The moksha middleware automatically
handles setting up this object, and making it available for all of the
applications and widgets.  Moksha utilizes `Doug Hellmann's feedcache module <http://www.doughellmann.com/projects/feedcache>`_, which intelligently handles
all of the hard work for us.

Here is an example of using the feed cache to manually fetch a feed.


.. code-block:: python

    import moksha
    feed = moksha.feed_cache.fetch('http://foo.com/feed.xml')
    for entry in feed.entries:
        print entry

.. note::
   The moksha.feed_cache object is a
   :class:`paste.registry.StackedObjectProxy` instance, and is setup by the
   :class:`moksha.middleware.MokshaMiddleware` before each request reaches
   your application.  Thus, it only works during requests and cannot be
   used without using the MokshaMiddleware.


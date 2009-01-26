Feeds
=====

Moksha makes it simple for applications and widgets to efficiently obtain
data from arbitrary RSS/Atom feeds.  The moksha Feed object transparently
handles the fetching, parsing, and caching of feeds, making it trivial to
pull in and manipulate external data sources in your application.

When used within the Moksha Platform, the Feed object will utilize the central
global `moksha.feed_cache`.  When used outside of the platform, it will
automatically use a local sqlite database cache.

API usage
---------

The Feed API provides a flexible Feed object that can be utilize in many ways.

Rendering a url with the Feed object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from moksha import Feed
    feed = Feed()
    feed(url='http://lewk.org/rss')

:Note: Usually you would instantiate a single Feed object somewhere in your project, and just call it with a `url` when rendering it in your templates.

Subclassing
~~~~~~~~~~~

You can easily subclass the Feed widget and provide your own url.

.. code-block:: python

    from moksha import Feed

    class MyFeed(Feed):
        url = 'http://foo.com/feed.xml'

    myfeed = MyFeed()
    myfeed() # renders the widget.  usually done in the template.

As a child Widget
~~~~~~~~~~~~~~~~~

By defining your Feeds as children to a widget, ToscaWidgets will automatically
handle setting a unique id for your Feed object, as well as giving you the
ability access it in your template from the `c` context object.

.. code-block:: python

    from tw.api import Widget
    from moksha import Feed

    class MyWidget(Widget):
        myfeedurl = 'http://foo.com/feed.xml'
        children = [Feed('myfeed', url=myfeedurl)]
        template = "${c.myfeed()}"

As a generator
~~~~~~~~~~~~~~

You can also utilize the Feed widget as a generator, giving you the ability
to iterate over the entries as necessary.

.. code-block:: python

    from moksha import Feed

    feed = Feed(url='http://foo.com/feed.xml')
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

:Note: The moksha.feed_cache object is a :class:`paste.registry.StackedObjectProxy` instance, and is setup by the :class:`moksha.middleware.MokshaMiddleware` before each request reaches your application.  Thus, it only works during requests and cannot be used without using the MokshaMiddleware.

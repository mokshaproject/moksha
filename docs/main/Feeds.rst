Feeds
=====

Moksha makes it simple for applications and widgets to efficiently obtain
data from arbitrary RSS/Atom feeds.  The moksha Feed object transparently
handles the fetching, parsing, and caching of feeds, making it trivial to
pull in and manipulate external data sources in your application.

API usage
---------

The Feed API provides a flexible Feed object that can be utilize in many ways.

Subclassing
~~~~~~~~~~~

You can easily subclass the Feed widget and provide your own url.

.. code-block:: python

    from moksha.widgets import Feed

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
    from moksha.widgets import Feed

    class MyWidget(Widget):
        myfeedurl = 'http://foo.com/feed.xml'
        children = [Feed('myfeed', url=myfeedurl)]
        template = "${c.myfeed()}"

As a generator
~~~~~~~~~~~~~~

You can also utilize the Feed widget as a generator, giving you the ability
to iterate over the entries as necessary.

.. code-block:: python

    from moksha.widgets import Feed

    feed = Feed(url='http://foo.com/feed.xml')
    for entry in feed.iterentries():
        print entry.title

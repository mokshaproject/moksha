============
Live Widgets
============

Moksha provides a :class:`LiveWidget` that handles automatically subscribing
your widget to a given message `topic`, or list of topics.  When the widget
receives a new message, the `onmessage` JavaScript callback will be run by the
client with JSON data in the `json` variable.

A basic LiveWidget
------------------

Below is an example of a really basic live widget.  This widget subscribes to
the 'stuff' message topic, and will perform an `alert` upon new messages.

.. code-block:: python

    from moksha.api.widgets.live import LiveWidget

    class MyLiveWidget(LiveWidget):
        topic = 'stuff'
        onmessage = 'alert(json);'
        template = "Hi, I'm a live widget!"


The Live Feed Widget
--------------------

.. code-block:: python

    from moksha.api.widgets.feed.live import LiveFeedWidget

.. widgetbrowser:: moksha.widgets.demos.LiveFeedDemo
   :tabs: demo, source, template, parameters
   :size: large

--------------------------------------------------------------------------------

Moksha provides an example :class:`LiveFeedWidget` that displays messages from the `feed_example` topic, using jQuery.

.. code-block:: python

    from moksha.api.widgets.live import LiveWidget
    from moksha.api.widgets.feed import Feed

    class LiveFeedWidget(LiveWidget):
        """ A live streaming feed widget """
        topic = 'feed_example'
        onmessage = """
            $.each(json, function() {
                $("#${id} ul li:last").remove();
                $("<li/>").hide().html(
                    $("<a/>")
                      .attr("href", this.link)
                      .text(this.title))
                  .prependTo($("#${id} ul"))
                  .show();
            });
        """
        template = '${feed()}'
        url = None

        def update_params(self, d):
            super(LiveFeedWidget, self).update_params(d)
            d['feed'] = Feed(d['id'], url=d.url)

Using the LiveFeedWidget
------------------------

.. code-block:: python

    from moksha.api.widgets.feed import LiveFeedWidget

    class MyLiveWidget(LiveFeedWidget):
        topic = 'feeds.myfeed'
        url = 'http://foo.com/bar.xml'

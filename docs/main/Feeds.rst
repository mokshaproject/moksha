=====
Feeds
=====

Moksha makes it simple for applications and widgets to efficiently obtain
data from arbitrary RSS/Atom feeds.  The moksha Feed object transparently
handles the fetching, parsing, and caching of feeds, making it trivial to
pull in and manipulate external data sources in your application.

When used within the Moksha Platform, the Feed object will utilize the central
global `moksha.feed_cache`.  When used outside of the platform, it will
automatically use a local sqlite database cache.

.. toctree::
   :maxdepth: 2

   FeedWidget
   FeedStream

The Moksha Feed Stream
----------------------

The ``mdemos.feeds`` app provides a moksha Producer_ that will handle
automatically fetching, parsing, and caching feeds.  Once installed, the Moksha Feed Stream will be run by the MokshaHub_.

It will automatically fetch all feeds used by the Moksha :class:`Feed` object,
as well as all feeds listed in a ``feeds.txt`` file, if one exists.

Installing the ``mdemos.feeds`` app
-----------------------------------

Currently the easiest way to install the app is from the git repository

.. code-block:: bash

   $ git clone git://github.com/ralphbean/mdemos.feeds
   $ cd mdemos.feeds


From here, if you are running Moksha from an RPM installation:

.. code-block:: bash

   $ paver reinstall

Or, if you're running from a virtualenv installation:

.. code-block:: bash

   $ paver install

Configuring the Moksha Feed Aggregator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The feed app can be configured with the following options in your config file:

.. code-block:: python

   # Enable the feed aggregator in the moksha-hub
   moksha.feedaggregator = True

   # Number of seconds between polling feeds
   feed.poll_frequency = 900

   # Where to store the feed caches. Defaults to an in-memory cache.
   #feed_cache = sqlite:///%(here)s/feeds.db

   # Max age (in seconds) of each feed in the cache
   feed.max_age = 300

   # Timeout in seconds for the web request
   feed.timeout = 60

   # The number of simultaneous connections
   feed.deferred_groups = 3


Performing post-processing on feed entries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All new feed entries for a given ``$URL`` are sent to the ``moksha.feeds.$URL``
message topic. By default only the title and url of the entry are sent to the
message broker.  However, Moksha provides a simple API for writing
post-processing plug-ins that can modify the feed before it is sent to any
:doc:`LiveWidgets` or :doc:`Consumers`.

.. code-block:: python

   def process_feed_entry(entry):
    """ This method is called by the Moksha Feed Streamer with each feed entry.

    Here is where we do post-processing on the entry before it gets serialized
    to JSON and send to our message broker, and then the users.

    :entry: A :mod:`feedparser` feed object
    """
    return dict(author=entry['author'],
                author_link=entry['author_detail']['href'],
                content=entry['content'][0]['value'],
                author_avatar=entry['source']['icon'])

Then you simply plug this method into the ``moksha.feeds.post_processor`` entry-point:

.. code-block:: python

   setup(...
         entry_points="""
           [moksha.feeds.post_processor]
           myfeedprocessor = myapp.feed_processor:process_feed_entry
         """
   )

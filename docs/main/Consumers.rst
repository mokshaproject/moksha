Consumers
=========

Moksha provides a simple API for creating "consumers" of message topics.

This means that your consumer is instantiated when the MokshaHub is initially
loaded, and receives each message for the specified topic through the
:meth:`Consumer.consume` method.  The `message` argument will be the body of
the actual message, decoded from JSON.

Creating
--------

.. code-block:: python

    from moksha.api.hub import Consumer

    class FeedConsumer(Consumer):
        topic = 'feeds'
        def consume(self, message):
            print message

.. note::

   The :class:`MokshaHub` currently executes each consumer in their own
   Thread, so be sure to employ thread-safety precausions when implementing
   your :class:`Consumer`.

Installing
----------

To "install" your consumer, you have to expose it on on the `moksha.consumer`
entry-point.  This can be done by updating your applications `setup.py` to
make it look something like this:

.. code-block:: python

        entry_points="""

        [moksha.consumer]
        feedconsumer = myapplication.feedconsumer:FeedConsumer

        """

After modifying your entry-points, you'll need to re-generate your project's `egg-info`.  The `start-moksha` script will do this for you.

.. code-block:: bash

    $ python setup.py egg_info


Moksha will now automatically detect, instantiate, and feed your consumer.

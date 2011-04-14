Consumers
=========

.. automodule:: moksha.api.hub.consumer

Creating
--------

.. code-block:: python

    from moksha.api.hub import Consumer

    class FeedConsumer(Consumer):

        # The topic to listen to.
        topic = 'moksha.feeds'

        # Automatically decode message as JSON, and encode when using self.send_message
        jsonify = True

        def consume(self, message):
            print message['topic']
            print message['body']

.. note::

   The :class:`MokshaHub` currently executes each consumer in their own
   Thread, so be sure to employ thread-safety precausions when implementing
   your :class:`Consumer`.

.. note::

   If your using AMQP, your `topic` can using wildcards.
   http://www.rabbitmq.com/faq.html#wildcards-in-topic-exchanges

   Wildcard topics do not work using STOMP.

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

After modifying your entry-points, you'll need to re-generate your project's `egg-info`.  A number of the `fabric` commands can do this for you, in particular:

.. code-block:: bash

    $ fab -H localhost egg_info

Alternatively, you can do it yourself.

.. code-block:: bash

    $ workon moksha
    $ python setup.py egg_info
    $ deactivate


Moksha will now automatically detect, instantiate, and feed your consumer.

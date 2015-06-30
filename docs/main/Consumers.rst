Consumers
=========

.. automodule:: moksha.hub.api.consumer

Creating
--------

.. code-block:: python

    from moksha.hub.api import Consumer

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

   If you're using AMQP, your `topic` can using wildcards.
   http://www.rabbitmq.com/faq.html#wildcards-in-topic-exchanges

   Wildcard topics do not work using STOMP.

.. note::

   If you're using 0mq and ``zmq_strict`` is set to False in your config file,
   then your topic will behave like it usually does with 0mq.  i.e.: `foo` will
   match `foobar`, `foobaz, and `foo`.  If ``zmq_strict`` is set to True then
   `foo` will match only `foo` and not `foobaz` or `foobar`.

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

.. note::

        You can also install a collection of consumers in the same manner.  Just
        specify the name of an iterable object in place of the consumer class
        name in the example above.  This even works with generator objects.

After modifying your entry-points, you'll need to re-generate your project's `egg-info`.

.. code-block:: bash

    $ workon moksha
    $ python setup.py egg_info
    $ deactivate


Moksha will now automatically detect, instantiate, and feed your consumer.

Consumers
=========

Moksha provides a simple API for creating "consumers" of message topics.

This means that your consumer is instantiated when the MokshaHub is initially
loaded, and receives each for the specified topic through the
:meth:`Consumer.consume` method.


.. code-block:: python

    from moksha.api.hub import Consumer

    class FeedConsumer(Consumer):
        topic = 'feeds'
        def consume(self, message):
            print message.body

:Note: The :class:`MokshaHub` currently executes each consumer in their own
       Thread, so be sure to employ thread-safety precausions when implementing
       your :class:`Consumer`.

To "install" your consumer, you have to expose it on on the `moksha.consumer`
entry-point.  This can be done by updating your applications `setup.py` to
make it look something like this:

.. code-block:: python

   from setuptools import setup, find_packages

   setup(
        name='myapplication',
        version='0.1',
        packages=find_packages(),
        entry_points="""

        [moksha.consumer]
        feedconsumer = myapplication.feedconsumer:FeedConsumer

        """
    )

After modifying your entry-points, you'll need to re-generate your project's `egg-info`.

.. code-block:: bash

    $ python setup.py egg_info


Moksha will now automatically detect, instantiate, and feed your consumer.

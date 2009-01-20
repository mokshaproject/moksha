"""
Consumers
=========

A `Consumer` is a simple consumer of messages.  Based on a given `routing_key`,
your consumer's :meth:`consume` method will be called with the message.

Example consumers:

    -tapping into a koji build, and sending a notification?
    - hook into a given RSS feed and save data in a DB?

Adding a new consumer
---------------------

Adding a new Consumer to Moksha is as easy as adding it to the `[moksha.consumer]`
entry-point in your `setup.py` file::

    [moksha.consumer]
    myconsumer = myproject.module:MyConsumer

"""


class Consumer(object):
    queue = None
    def consume(self, message):
        raise NotImplementedError

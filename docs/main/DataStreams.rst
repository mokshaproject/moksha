============
Data Streams
============

Moksha offers a :class:`DataStream` API that allows you to easily provide
data to your message brokers.  DataStreams are loaded and run by the :class:`MokshaHub`, isolated from the WSGI application.

The DataStreams contain a connection to the MokshaHub via the `self.hub`
object.  It also provides a `send_message(topic, message)` method that will
send your message to the hub.

Polling Data Streams
--------------------

The :class:`PollingDataStream` will automatically wake up at a given `frequency` (which can be a `datetime.timedelta` object, or the number of a seconds), and call the :meth:`poll` method.

Below is an example of a :class:`PollingDataStream` that wakes up every 10 seconds, and sends a 'Hello World!' message to the 'hello' `topic`.

.. code-block:: python

    from datetime import timedelta
    from moksha.api.streams import PollingDataStream

    class HelloWorldDataStream(PollingDataStream):
        frequency = timedelta(seconds=10)

        def poll(self):
            self.send_message('hello', 'Hello World!')

Installing
----------

To install your `DataStream`, simply add it to the `[moksha.stream]` entry-point
in your `setup.py`, like so:

.. code-block:: python

    [moksha.stream]
    hello = myproject.streams.hello:HelloWorldDataStream

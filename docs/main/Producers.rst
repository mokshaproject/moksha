=========
Producers
=========

Moksha offers a :class:`Producer` API that allows you to easily provide data to
your message brokers.  Producers are loaded and run by the :class:`MokshaHub`,
isolated from the WSGI application.

The Producers contain a connection to the MokshaHub via the `self.hub` object.
It also provides a `send_message(topic, message)` method that will send your
message to the hub.

Polling Producers
------------------

The :class:`PollingProducer` will automatically wake up at a given `frequency`
(which can be a `datetime.timedelta` object, or the number of a seconds), and
call the :meth:`poll` method.

Below is an example of a :class:`PollingProducer` that wakes up every 10
seconds, and sends a 'Hello World!' message to the 'hello' `topic`.

.. code-block:: python

    from datetime import timedelta
    from moksha.hub.api.producer import PollingProducer

    class HelloWorldProducer(PollingProducer):
        frequency = timedelta(seconds=10)

        def poll(self):
            self.send_message('hello', 'Hello World!')

Installing
----------

To install your `Producer`, simply add it to the `[moksha.producer]` entry-point
in your `setup.py`, like so:

.. code-block:: python

    [moksha.producer]
    hello = myproject.producers:HelloWorldProducer

.. note::

    Just as with consumers, you can also expose a collection of producers by
    creating a list, generator object, etc. inside of your code and providing
    that variable as an entry-point under `[moksha.producer]`.

======
Topics
======

A `"Topic"` in Moksha is basically just a message queue.

By abstracting out the low-level messaging protocols and brokers, Moksha
applications can interact with `"topics"` without having to worry about the
underlying technology that is involved.  For example, a `topic` could
potentially be represented by a STOMP destination, an AMQP message
queue, or a 0mq filter.  These messaging backends can be swapped out
and configured without having to alter the applications that care
about those `topics`.

For details on how to interact with topics, see the documentation on :doc:`Consumers`, :doc:`Producers`, and :doc:`MokshaHub`.

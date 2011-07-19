===================
Data Interpretation
===================

Moksha provides various mechanisms that allow applications to more easily interpret
dynamic data and act on it.

Collaborative glue
------------------

Although it does not yet, Moksha will allow anything to be
tagged, shared, discussed, annotated, rated, etc.

Live streams
------------

Any data source, even if moksha has to occasionally poll it, can be displayed
as a 'live' widget.  "Data streams", or Producers,  can also easily expose
themselves through an AMQP or STOMP message queue, allowing other applications
and services to interact with new data, as it is discovered.

Consumers
---------

Moksha allows plugins to monitor arbitrary message `"topics"`, giving
developers the ability to register actions on arbitrary events.

Extension Points
----------------

Moksha gives developers the ability to add additional functionality to predictable
patterns found within dynamic data streams.  For example, an extension point
could find all occurences of known project names within a data feed, and easily
turn them into a dynamic hover menu that could display related data.

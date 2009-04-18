===================
Data Interpretation
===================

Moksha provides various mechanisms that allows applications to easily interpret
dynamic data, along with adding additional functionality to it.

Collaborative glue
------------------

Moksha will allow anything to be tagged, shared, discussed, annotated, rated,
etc.

Live streams
------------

Any data source, even if moksha has to occasionally poll it, can be displayed
as a 'live' widget.  "Data streams", or Producers,  can also easily expose
themselves through an AMQP or STOMP message queue, allowing other applications
and services to interact with new data, as it is discovered.

Consumers
---------

Moksha allows plugins to monitor arbitrary message `"topics"`, giving
developers the ability to perform various actions upon various events.

Extension Points
----------------

Gives developers the ability to add additional functionality to predictable
patterns found within dynamic data streams.  For example, an extension point
could find all occurences of known project names within a data feed, and easily
turn them into a dynamic hover menu that could display related data.

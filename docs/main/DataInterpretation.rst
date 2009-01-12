===================
Data Interpretation
===================

Moksha provides various mechanisms that allows applications to easily interpret dynamic data, along with adding additional functionality to it.

Collaborative glue
------------------

Moksha will allow anything to be tagged, shared, discussed, annotated, rated,
etc.

Extension Points
----------------

Gives developers the ability to add additional functionality to predictable
patterns found within dynamic data streams.  For example, an extension point
could find all occurences of known project names within a data feed, and easily
turn them into a dynamic hover menu that could display related data.

Live streams
------------

Any data source, even if moksha has to occasionally poll it, can be displayed
as a 'live' widget on any web site.  Data streams can also easily expose
themselves through a AMQP message queue, allowing other applications and
services to interact with new data, as it is discovered.

Hooks
-----

Moksha allows plugins to monitor arbitrary AMQP message queues, giving
developers the ability to perform various actions upon various events.

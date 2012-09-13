Data Visualization
==================

Moksha makes it simple to write widgets that can efficiently acquire data in
"real-time", and display it to the user.

Live Widgets
------------

Moksha provides a :class:`moksha.wsgi.widgets.api.LiveWidget` class that
allows developers to create widgets that can subscribe to message "topics".
Upon arrival of new messages, Moksha will automatically pass this data to your
widget, allowing you to create rich "real-time" web applications.

As mentioned before, Moksha supports a number of underlying transports for this
including COMET (with a full javascript in-browser AMQP library) and
the soon-to-be-standard Websocket protocol.

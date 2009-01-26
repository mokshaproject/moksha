Data Visualization
==================

Moksha makes it simple to write widgets that can efficiently acquire data in
"real-time", and display it to the user.

Live Widgets
------------

Moksha provides a :class:`LiveWidget` class that allows developers to create
widgets that can subscribe to message "topics".  Upon arrival of new messages,
Moksha will automatically pass this data to your widget, allowing you to create
rich "real-time" web applications.

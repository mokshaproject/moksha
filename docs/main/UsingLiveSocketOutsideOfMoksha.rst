Using Moksha's real-time pipes outside of Python
================================================

Want to add realtime functionality to your existing web site, but don't want to
have to learn Python or TurboGears?

Thankfully, Moksha allows you to leverage it's realtime pipes on any existing
web page without having to write a line of Python code.

This means that you can have your web site listen to topics from your message
broker, and run javascript when new messages arrive.

Subscribing to real-time message streams
----------------------------------------

All you need to do is add a single ``<script>`` tag to your web site that
specifies the topic that you wish to listen to, and the javascript function
that should be called with each new message as they arrive.

The Moksha live socket will automatically handle decoding the message body to
JSON before passing it to your callback.

.. code-block:: html

   <html>
       <head>
           <script src="http://code.jquery.com/jquery-latest.min.js"></script>
       </head>
       <body>
           <ul id="data"/>
       </body>
       <script>
           function consume_message(json) {
               $('<li/>').text(json.msg).appendTo('#data')
           }
       </script>
       <script type="text/javascript" src="http://localhost:8080/livesocket?topic=helloworld&callback=consume_message"></script>
   </html>


Sending messages to the broker
------------------------------

You can easily send messages to a given topic using the ``moksha.send_message``
function.  This function will automatically handle converting your javascript
objects to JSON for you.

.. code-block:: html

   <a href="#" onclick="moksha.send_message('helloworld', {'msg': 'Hi there!'});">Send message</a>


.. note::

   In order for the live sockets to work properly, Moksha (specifically
   Orbited) must be running under the same domain as your web site.

.. note::

   You can disable the automatic JSON encoding/decoding by passing
   ``json=False`` to the livesocket URL.

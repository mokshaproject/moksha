Using Moksha's real-time pipes outside of Python
================================================

Want to add realtime functionality to your existing web site, but don't want to
have to learn Python or TurboGears?

Thankfully, Moksha allows you to leverage it's realtime pipes on any existing
web page without having to write a line of Python code.

This means that you can have your web site listen to topics from your message
broker, and run javascript when new messages arrive.

All you need to do is add a single ``<script>`` tag to your web site that
specifies the topic that you wish to listen to, and the javascript function
that should be called with each new message as they arrive.

.. code-block:: html

   <html>
       <head>
           <script src="http://code.jquery.com/jquery-latest.min.js"></script>
       </head>
       <body>
           <ul id="data"/>
       </body>
       <script>
           function consume_message(msg) {
               $('<li/>').text(msg).appendTo('#data')
           }
       </script>
       <script type="text/javascript" src="http://localhost:8080/livesocket?topic=helloworld&callback=consume_message"></script>
   </html>

.. note::

   In order for the live sockets to work properly, Moksha (specifically Orbited) must be running
   under the same domain as your web site.

Using Moksha's real-time pipes outside of Python
================================================

Want to add realtime functionality to your existing web site, but don't want to
have to learn Python or TurboGears?

Thankfully, Moksha allows you to leverage it's realtime pipes on any existing
web page without having to write a line of Python code.

Add code snippet to your web page
Configure your message broker
Start Moksha

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

Caveats
-------

Must be under the same domain name.

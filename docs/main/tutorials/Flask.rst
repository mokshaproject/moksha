===================================
Moksha+Flask - Hello World Tutorial
===================================

.. note:: You can find the source for this tutorial `on github
   <http://github.com/mokshaproject/moksha-flask-hello_world>`_.

Bootstrapping
-------------

Set up a virtualenv and install Moksha and Pyramid (install
`virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_ if you haven't already).

.. code-block:: bash

    $ mkvirtualenv tutorial
    $ pip install Flask
    $ pip install moksha.wsgi moksha.hub
    $ mkdir tutorial
    $ cd tutorial

Copy this dummy flask a file called ``tutorial.py``.
It may `look familiar to you <http://flask.pocoo.org/>`_.

.. code-block:: python

   from flask import Flask
   app = Flask(__name__)

   @app.route("/")
   def hello():
       return "Hello World!"

   if __name__ == "__main__":
       app.run()

Give it a run to see if it works:

.. code-block:: bash

    python tutorial.py

Visit http://localhost:5000 to check it out.  Success.

Add a configuration file
------------------------

Create a ``development.ini`` file with the following contents::

    [app:main]
    #moksha.domain = live.example.com
    moksha.domain = localhost

    moksha.notifications = True
    moksha.socket.notify = True

    moksha.livesocket = True
    moksha.livesocket.backend = websocket
    #moksha.livesocket.reconnect_interval = 5000
    moksha.livesocket.websocket.port = 9998

    zmq_enabled = True
    #zmq_strict = True
    zmq_publish_endpoints = tcp://*:3000
    zmq_subscribe_endpoints = tcp://127.0.0.1:3000


Enable ToscaWidgets2 and Moksha Middlewares
-------------------------------------------

Wrap your app in `WSGI middleware
<http://flask.pocoo.org/docs/quickstart/#hooking-in-wsgi-middlewares>`_ by
first adding the following imports to the top of your file:

.. code-block:: python

   from moksha.common.lib.helpers import get_moksha_appconfig
   from moksha.wsgi.middleware import make_moksha_middleware
   from tw2.core.middleware import make_middleware

And also edit the ``if __name__ == "__main__":`` section to look like this:

.. code-block:: python

    if __name__ == "__main__":
        # Load development.ini
        config = get_moksha_appconfig()

        # Wrap the inner wsgi app with our middlewares
        app.wsgi_app = make_moksha_middleware(app.wsgi_app, config)
        app.wsgi_app = make_middleware(app.wsgi_app)

        app.run()

You now have two new pieces of WSGI middleware floating under your Flask
app.  Neat!  Restart the app and check http://localhost:5000 to make sure
its not crashing.

.. see-also::

   - :doc:`Middleware`

Your first Polling Producer
---------------------------


Go back and edit ``tutorial.py`` and add the following definition:

.. code-block:: python

    import datetime
    import moksha.hub.api.producer

    class HelloWorldProducer(moksha.hub.api.producer.PollingProducer):
        frequency = datetime.timedelta(seconds=2)

        def poll(self):
            self.send_message('hello_world', "Hello World!")

Moksha's ability to find producers and consumers is dependent on
setuptools, so you'll need to add a ``setup.py`` file with the
following contents:

.. code-block:: python

    from setuptools import setup
    setup(
        name='tutorial',
        entry_points="""
        [moksha.producer]
        hello = tutorial:HelloWorldProducer
        """,
    )

Open up a **second** terminal, activate your virtualenv with ``workon
tutorial`` and run the ``moksha-hub``:

.. code-block:: bash

    $ workon tutorial
    $ python setup.py develop
    $ moksha-hub


This will start up the hub which should pick up and load your
``HelloWorldProducer``.  Keep this running in your second terminal
as you go on to create the frontend components.

Your first LiveWidget
---------------------

Edit ``tutorial.py`` again and add the three following imports at the top:

.. code-block:: python

   import moksha.wsgi.widgets.api
   import tw2.jqplugins.gritter
   import flask.templating

Add the following widget definiton:

.. code-block:: python

    import moksha.wsgi.widgets.api
    import tw2.jqplugins.gritter

    class PopupNotification(moksha.wsgi.widgets.api.LiveWidget):
        topic = "*"
        onmessage = "$.gritter.add({'title': 'Received', 'text': json});"
        resources = moksha.wsgi.widgets.api.LiveWidget.resources + \
                tw2.jqplugins.gritter.gritter_resources
        backend = "websocket"

        # Don't actually produce anything when you call .display() on this widget.
        inline_engine_name = "mako"
        template = ""

Finally, you need to expose this widget through a Flask route.  Blow away the
existing ``def hello()`` route and replace it with the following:

.. code-block:: python

    simple_template = """
    <html>
    <head></head>
    <body>
    Really?
    {{notification_widget.display()}}
    {{moksha_socket.display()}}
    </body>
    </html>
    """


    @app.route("/")
    def hello():
        config = get_moksha_appconfig()
        socket = moksha.wsgi.widgets.api.get_moksha_socket(config)
        return flask.templating.render_template_string(
            simple_template,
            notification_widget=PopupNotification,
            moksha_socket=socket,
        )

Go restart your app (make sure ``moksha-hub`` is running in a second terminal) and check out
http://localhost:5000 again.  You should see popups from your PollingProducer.

.. see-also::

   - :doc:`LiveWidget`

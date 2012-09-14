=====================================
Moksha+Pyramid - Hello World Tutorial
=====================================

.. note:: You can find the source for this tutorial `on github
   <http://github.com/mokshaproject/moksha-pyramid-hello_world>`_.

Bootstrapping
-------------

Set up a virtualenv and install Moksha and Pyramid (install
`virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_ if you haven't already).

.. code-block:: bash

    $ mkvirtualenv tutorial
    $ pip install pyramid
    $ pip install moksha.wsgi moksha.hub
    $ # Also, install weberror for kicks.
    $ pip install weberror

Use ``pcreate`` to setup a Pyramid scaffold, install dependencies,
and verify that its working.  I like the ``alchemy`` scaffold, so we'll use that
one.

.. code-block:: bash

    $ pcreate -t alchemy tutorial
    $ cd tutorial/
    $ rm production.ini  # moksha-hub gets confused when this is present.
    $ python setup.py develop
    $ initialize_tutorial_db development.ini
    $ pserve --reload development.ini

Visit http://localhost:6543 to check it out.  Success.

Enable ToscaWidgets2 and Moksha Middlewares
-------------------------------------------

Go and edit ``development.ini``.  There should be a section at the top named
``[app:main]``.  Change that to ``[app:tutorial]``.  Then, just above the
``[server:main]`` section add the following three blocks::

    [pipeline:main]
    pipeline =
        egg:WebError#evalerror
        tw2
        moksha
        tutorial

    [filter:tw2]
    use = egg:tw2.core#middleware

    [filter:moksha]
    use = egg:moksha.wsgi#middleware

You now have three new pieces of WSGI middleware floating under your pyramid
app.  Neat!  Restart pserve and check http://localhost:6543 to make sure
its not crashing.

.. seealso::

   - :doc:`Middleware`

Provide some configuration for Moksha
-------------------------------------

Edit ``development.ini`` and add the following lines in the ``[app:tutorial]`` section.  Do it just under the ``sqlalchemy.url`` line::

    ##moksha.domain = live.example.com
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

Your first Polling Producer
---------------------------

Add a new file in ``tutorial/producers.py``.  In it, add the following definition:

.. code-block:: python

    import datetime
    import moksha.hub.api.producer


    class HelloWorldProducer(moksha.hub.api.producer.PollingProducer):
        frequency = datetime.timedelta(seconds=2)

        def poll(self):
            self.send_message('hello_world', "Hello World!")

As well, edit ``setup.py`` and modify the ``entry_points`` section to include a
declaration of this new producer like so::

    [moksha.producer]
    hello = tutorial.producers:HelloWorldProducer

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

Create a new file in ``tutorial/widgets.py``.  In it, add the following
definition:

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

You'll need to expose this widget and the moksha global resources to your
templates.  You could do this with Pyramid's `events` infrastructure and inject
them into every page that gets served, but we'll just dumbly expose them in the
default ``/home`` view for this scaffold.

Edit ``tutorial/views.py`` and add the following imports at the top:

.. code-block:: python

    import tutorial.widgets
    from moksha.wsgi.widgets.api import get_moksha_socket

In the same file, change the ``return`` statement of ``my_view()`` to return the
following:

.. code-block:: python

   return {
       'one':one,
       'project':'tutorial',
       'notification_widget': tutorial.widgets.PopupNotification,
       'moksha_socket': get_moksha_socket(request.registry.settings),
   }

Finally, display the widget on your page by editing
``tutorial/templates/mytemplate.pt`` and adding the following at the end
but just inside of the ``</body>`` tag::

    <div tal:content="structure notification_widget.display()"></div>
    <div tal:content="structure moksha_socket.display()"></div>

Go restart your ``pserve`` server and check out http://localhost:6543 again.
You should see popups from your PollingProducer.

.. seealso::

   - :doc:`LiveWidget`

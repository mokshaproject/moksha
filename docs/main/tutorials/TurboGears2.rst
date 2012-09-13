=========================================
Moksha+TurboGears2 - Hello World Tutorial
=========================================

.. note:: You can find the source for this tutorial `on github
   <http://github.com/mokshaproject/moksha-turbogears2-hello_world>`_.

Bootstrapping
-------------

Set up a virtualenv and install Moksha and TurboGears2 (install
`virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_ if you haven't already).

.. code-block:: bash

    $ mkvirtualenv tutorial
    $ pip install -i http://tg.gy/current tg.devtools
    $ pip install moksha.wsgi moksha.hub

Use paster to setup the default TurboGears2 quickstart, install dependencies,
and verify that its working.

.. code-block:: bash

    $ paster quickstart --auth --mako --sqlalchemy -p tutorial tutorial
    $ cd tutorial/
    $ python setup.py develop
    $ nosetests
    $ paster setup-app development.ini
    $ paster serve development.ini

Visit http://localhost:8080 to check it out.  Success.

Enable ToscaWidgets2
--------------------

Some versions of TurboGears2 start with ToscaWidgets1 turned on by default.
You'll want to disable that and enable ToscaWidgets2.

Edit ``tutorial/config/app_cfg.py`` and add the following two lines to the bottom.

.. code-block:: python

   base_config.use_toscawidgets = False
   base_config.use_toscawidgets2 = True


Enabling the Moksha Middleware
------------------------------

Edit ``tutorial/config/middleware.py`` and remove the line that reads
``app = make_base_app(global_conf, full_stack=True, **app_conf)``.  In its
place, put the following

.. code-block:: python

   from moksha.wsgi.middleware import make_moksha_middleware
   wrap_app = lambda app: make_moksha_middleware(app, app_conf)
   app = make_base_app(global_conf, full_stack=True,
                       wrap_app=wrap_app, \*\*app_conf)

.. see-also::

   - :doc:`Middleware`

Provide some configuration for Moksha
-------------------------------------

Edit ``development.ini`` and add the following lines under the main section::

    moksha.domain = localhost

    moksha.livesocket = True
    moksha.livesocket.backend = websocket
    moksha.livesocket.websocket.port = 9998

    moksha.socket.notify = True

    zmq_enabled = True
    zmq_strict = False
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
templates.  You could do this with some logic in a controller, but instead
will just stuff it on every page for simplicity here.

Edit ``tutorial/lib/base.py`` and add the following **inside** the ``__call__``
method:

.. code-block:: python

    import tutorial.widgets
    from moksha.wsgi.ext.turbogears import global_resource

    tmpl_context.notification_widget = tutorial.widgets.PopupNotification
    tmpl_context.moksha_global_resources = global_resources

Finally, display the widget on your page by editing
``tutorial/templates/master.mak`` and adding the following at the end but just
inside of the ``</body>`` tag::

    ${tmpl_context.notification_widget.display() |n}
    ${tmpl_context.moksha_global_resources() | n}

Go restart your ``paster`` server and check out http://localhost:8080 again.
You should see popups from your PollingProducer.

.. see-also::

   - :doc:`LiveWidget`



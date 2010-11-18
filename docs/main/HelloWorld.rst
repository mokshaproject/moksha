=======================
Hello World Moksha Demo
=======================

The goal of this tutorial is to show the simplicity of Moksha's API by creating
basic "Hello World" components in one demo.

:Demo Source: https://fedorahosted.org/moksha/browser/demo

The Controller
--------------

This is the most basic of controllers.

`demo/controllers/root.py`

.. code-block:: python

   from tg import expose

   class Root(object):

       @expose()
       def index(self):
           return 'Hello World!'


Ok, so here we have a trivial TurboGears controller.  How do we plug this into
Moksha and actually run it?

Let's say we want this index method to be the root of our application.  To
accomplish this we add it to the `[moksha.root]` entry-point in our setup.py::

    [moksha.root]
    root = demo.controllers.root:Root


.. seealso::

   :doc:`PluginEntryPoints`

Running the Moksha stack
------------------------

.. code-block:: bash

   $ moksha start

.. code-block:: bash

   $ curl http://localhost:8080/
   Hello World


.. seealso::

   :doc:`MokshaCLI`

Bringing a templating engine into the mix
-----------------------------------------

The previous example just returned a string from our controller.  What if we
want to use one of the many powerful templating engines out there?

TurboGears supports a variety of engines, including Genshi, Mako, Jinja, etc.

So, lets create a dead simple Mako template.

`demo/templates/template.mak`

.. code-block:: html

   <html>
     <head><title>${msg}</title></head>
     <body>${msg}</body>
   </html>


Now let's plug in our Mako template into our Root controller.

.. code-block:: python

   @expose('mako:demo.templates.template')
   def index(self):
       """ An example controller method exposed with a Mako template """
       return {'msg': 'Hello World!'}


Building a basic Widget
-----------------------

.. image:: ../_static/widget.png

.. code-block:: python

   from tw.api import Widget

   class HelloWorldWidget(Widget):
       params = ['msg']
       msg = 'Hello World'
       template = '${msg}'
       engine_name = 'mako'

       def update_params(self, d):
           """ Render-time logic """
           super(HelloWorldWidget, self).update_params(d)


`setup.py`

.. code-block:: python

   [moksha.widget]
   helloworld = demo.widgets:HelloWorldWidget

.. code-block:: bash

   $ curl http://localhost:8080/widgets/basic

.. code-block:: html

   <html>
     <head></head>
     <body>Hello World</body>
   </html>

.. code-block:: bash

   $ curl http://localhost:8080/widgets/basic?msg=foobar

.. code-block:: html

   <html>
     <head></head>
     <body>foobar</body>
   </html>

.. seealso::

    :doc:`Widgets`



Creating a message producer
---------------------------

.. code-block:: python

   from datetime import timedelta
   from moksha.api.hub.producer import PollingProducer

   class HelloWorldProducer(PollingProducer):
       frequency = timedelta(seconds=3)

       def poll(self):
           self.send_message('helloworld', {'msg': 'Hello World!'})

.. seealso::

   :doc:`Messaging`

.. seealso::

   :doc:`Producers`

Creating a message consumer
---------------------------

`demo/consumer.py`

.. code-block:: python

   from moksha.api.hub.consumer import Consumer
   from demo.model import HelloWorldModel

   class HelloWorldConsumer(Consumer):
       topic = 'helloworld'

       def consume(self, message):
           self.log.info('Received message: ' + message['body']['msg'])

.. seealso::

   :doc:`Consumers`

Running the Moksha Hub
----------------------

.. image:: ../_static/moksha-hub.png

<consumer output>

.. seealso::

   :doc:`MokshaHub`

Creating a Live Widget!
-----------------------

Ok, on to the fun stuff.

Moksha provides an API for creating "live widgets".  A widget is a re-usable
bundle of HTML/JavaScript/CSS/Server-side logic   Making it "live" entails
having the widget "subscribe" to "topics" and perform some action upon 
new messages as they arrive in the users web browser.

.. image:: ../_static/live_widgets.png

`demo/widget.py`

.. code-block:: python

   from moksha.api.widgets.live import LiveWidget

   class HelloWorldWidget(LiveWidget):
       topic = "helloworld"
       template = """
           <b>Hello World Widget</b>
           <ul id="data"/>
       """
       onmessage = """
           $('<li/>').text(json.msg).prependTo('#data');
       """

<add to entry point>

<rendering the widget>

.. code-block:: python

   @expose('mako:moksha.templates.widget')
   def livewidget(self):
       tmpl_context.widget = moksha.get_widget('helloworld')
       tmpl_context.moksha_socket = moksha.get_widget('moksha_socket')
       return dict(options={})


.. seealso::

   :doc:`LiveWidget`

Creating a database model
-------------------------

`demo.model.model.py`

.. code-block:: python

   from datetime import datetime
   from sqlalchemy import Integer, Text, DateTime, Column
   from demo.model import DeclarativeBase

   class HelloWorldModel(DeclarativeBase):
       __tablename__ = 'helloworld'

       id = Column(Integer, autoincrement=True, primary_key=True)
       message = Column(Text)
       timestamp = Column(DateTime, default=datetime.now)

.. seealso::

   `Working with SQLAlchemy and your data model <http://turbogears.org/2.1/docs/main/SQLAlchemy.html>`_

Populating our database
~~~~~~~~~~~~~~~~~~~~~~~
<via the consumer upon message arrival>

.. code-block:: python

   from moksha.api.hub.consumer import Consumer
   from demo.model import HelloWorldModel

   class HelloWorldConsumer(Consumer):
       topic = 'helloworld'
       app = 'helloworld'

       def consume(self, message):
           self.log.info('Received message: ' + message['body']['msg'])

           entry = HelloWorldModel()
           entry.message = message['body']['msg']
           self.DBSession.add(entry)
           self.DBSession.commit()


Querying our database
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from demo.model import DBSession, HelloWorldModel

   class Root(object):

      @expose('mako:demo.templates.model')
      def model(self, *args, **kwargs):
          entries = DBSession.query(HelloWorldModel).all()
          return dict(entries=entries)

.. seealso::

   `SQLAlchemy documentation <http://www.sqlalchemy.org/docs>`_

Caching
-------

.. code-block:: python

   from pylons import cache
   from demo.model import DBSession, HelloWorldModel

   class Root(object):

       @expose('mako:demo.templates.model')
       def model(self):
           mycache = cache.get_cache('helloworld')
           entries = mycache.get_value(key='entries', createfunc=self._get_entries,
                                       expiretime=3600)
           return dict(entries=entries)

       def _get_entries(self, *args, **kwargs):
           return DBSession.query(HelloWorldModel).all()

.. seealso::

   `Caching in TurboGears2 <http://turbogears.org/2.1/docs/main/Caching.html>`_

.. seealso::

   `Beaker documentation <http://beaker.groovie.org>`_

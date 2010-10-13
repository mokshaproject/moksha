=======================
Hello World Moksha Demo
=======================

Ok, lets get down to the basics.

The goal of this tutorial is to show the simplicity of Moksha's API by creating
basic "Hello World" components in one demo.

<link to directory of code and tarball>

The Controller
--------------

This is the most basic of controllers.

demo/controllers/root.py

.. code-block:: python

   from tg import expose

   class Root(object):

       @expose()
       def index(self, *args, **kwargs):
           return 'Hello World!'


Ok, so here we have a trivial TurboGears controller.  How do we plug this into Moksha and actually run it?

Let's say we want this index method to be the root of our application.  To accomplish this we add it to the `[moksha.root]` entry-point in our setup.py::

    [moksha.root]
    root = demo.controllers.root:Root


Running the Moksha stack
------------------------

.. code-block:: bash

   $ moksha start

.. code-block:: bash

   $ curl http://localhost:8080/
   Hello World

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
   def index(self, *args, **kwargs):
       """ An example controller method exposed with a Mako template """
       return {'msg': 'Hello World!'}


** Messaging

Creating a message producer
---------------------------

Creating a message consumer
---------------------------

Creating a Live Widget!
-----------------------

Ok, on to the fun stuff.

Moksha provides an API for creating "live widgets".  A widget is a re-usable
bundle of HTML/JavaScript/CSS/Server-side logic   Making it "live" entails
having the widget "subscribe" to "topics" and perform some action upon 
new messages as they arrive in the users web browser.

<live widget diagram?>

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
   def livewidget(self, *args, **kwargs):
       tmpl_context.widget = moksha.get_widget('helloworld')
       tmpl_context.moksha_socket = moksha.get_widget('moksha_socket')
       return dict(options={})


Creating a database model
-------------------------

Caching
-------

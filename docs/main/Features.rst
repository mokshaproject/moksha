===============
Moksha Features
===============

WSGI Middleware Stack
---------------------
Moksha provides a `WSGI <http://wsgi.org>`_ (`PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_) compliant application and `middleware <http://www.wsgi.org/wsgi/Middleware_and_Utilities>`_ stack

Moksha was once highly coupled with the TurboGears2 framework, but has since
been separated.  You can concievably use Moksha's WSGI middleware and Widget
API with any WSGI framework such as `TurboGears2`, `Pyramid`, or
`Flask`.

.. seealso::

   - :doc:`Middleware`
   - :doc:`tutorials/TurboGears2`
   - :doc:`tutorials/Pyramid`
   - :doc:`tutorials/Flask`

Messaging Hub
-------------

Moksha provides a message hub that allows for other applications, services, or users to communicate over a low-latency topic-based publish/subscribe message bus.  It's designed in such a way as to facilitate a variety of different message flows, allowing for a combination of different message queueing brokers and protocols.

Out of the box, Moksha utilizes `MorbidQ <http://www.morbidq.com/>`_, a lightweight message queue for bundled deployment, for it's message queueing needs.  With a 1-line change to Moksha's configuration file, you can integrate it with an existing `AMQP <http://amqp.org/>`_ broker, such as `Qpid <http://incubator.apache.org/qpid/>`_ or `RabbitMQ <http://rabbitmq.com>`_.  With similarly small configuration changes, you can integrate it with a `0mq <http://www.zeormq.org>`_ messaging fabric.

.. seealso::

   - :doc:`MokshaHub`
   - :doc:`Producers`
   - :doc:`Consumers`

Low-latency Browser Socket
--------------------------

Moksha integrates with `Orbited <http://orbited.org>`_, a highly-scalable
server that allows for asynchronous browser <-> server communication (Comet).  Moksha
then makes it simple to create :doc:`LiveWidgets` that can publish and
subscribe to arbitrary message topics in the :doc:`MokshaHub`.  This
allows for the creation of very rich live web applications.

Moksha also packs a built-in WebSocket server and Live Widget mixin as an
alternative to the Orbited (Comet) pattern.  The WebSocket pattern is compatible
with only the 0mq messaging backend.

Plugin Infrastructure
---------------------

Moksha offers a highly-scalable plugin infrastructure that transparently
handles initializing, dispatching, manipulating, and scaling applications and
widgets -- allowing people to rapidly innovate without worrying about the
over or under-lying software architecture.

.. seealso::

   - :doc:`PluginEntryPoints`
   - :doc:`QuickstartTemplates`

Widget Creation API
-------------------

`ToscaWidgets <http://toscawidgets.org>`_ provides a powerful API for creating
reusable "Widgets", which are essentially just bundles of HTML, JavaScript,
CSS, and render-time logic.  Moksha once supported tw1 as well as tw2, but now
supports only the later for simplicity's sake.

Moksha also provides a variety of other Widgets, including a :doc:`LiveWidget`
API for creating real-time message-driven widgets that can publish and
subscribe to message :doc:`Topics`.

.. seealso::

   :doc:`Widgets`

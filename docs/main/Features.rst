===============
Moksha Features
===============

.. image:: ../_static/moksha-features.png

WSGI Middleware Stack
---------------------
Moksha provides a `WSGI <http://wsgi.org>`_ (`PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_) compliant application and `middleware <http://www.wsgi.org/wsgi/Middleware_and_Utilities>`_ stack


.. seealso::

   :doc:`Middleware`

Messaging Hub
-------------

Moksha provides a message hub that allows for other applications, services, or users to communicate over a low-latency topic-based publish/subscribe message bus.  It's designed in such a way as to facilitate a variety of different message flows, allowing for a combination of different message queueing brokers and protocols.

Out of the box, Moksha utilizes `MorbidQ <http://www.morbidq.com/>`_, a lightweight message queue for bundled deployment, for it's message queueing needs.  With a 1-line change to Moksha's configuration file, you can integrate it with an existing `AMQP <http://amqp.org/>`_ broker, such as `Qpid <http://incubator.apache.org/qpid/>`_ or `RabbitMQ <http://rabbitmq.com>`_.

.. seealso::

   :doc:`MokshaHub`

Low-latency Browser Socket
--------------------------

Moksha integrates with `Orbited <http://orbited.org>`_, a highly-scalable
server that allows for asynchronous browser <-> server communication (Comet).  Moksha
then makes it simple to create :doc:`LiveWidgets` that can publish and
subscribe to arbitrary message topics in the :doc:`MokshaHub`.  This
allows for the creation of very rich live web applications.

Plugin Infrastructure
---------------------

Moksha offers a highly-scalable plugin infrastructure that transparently
handles initializing, dispatching, manipulating, and scaling applications and
widgets -- allowing people to rapidly innovate without worrying about the
over or under-lying software architecture.

.. seealso::

   :doc:`PluginEntryPoints`
   :doc:`QuickstartTemplates`

Widget Creation API
-------------------

`ToscaWidgets <http://toscawidgets.org>`_ provides a powerful API for creating
reusable "Widgets", which are essentially just bundles of HTML, JavaScript,
CSS, and render-time logic.  The ToscaWidgets WSGI Middleware is also integrated
into Moksha, which handles intelligently injecting Widget resources.  Moksha
has built-in support for both ToscaWidgets1 and ToscaWidgets2.

Moksha also provides a variety of other Widgets, including a :doc:`LiveWidget`
API for creating real-time message-driven widgets that can publish and
subscribe to message :doc:`Topics`.

.. seealso::

   :doc:`Widgets`

Resource Connectors
-------------------

Moksha offers a Resource Layer that trivializes interacting with external
services in an intelligent and efficient manner.

.. seealso::

   :doc:`Connectors`

Highly Scalable Architecture
----------------------------

Moksha architecture is self-scaling and can adapt to a variety of
infrastructure environments.

Expert System
--------------

:doc:`MokshaHub` gives you Expert System-like functionality by providing
APIs for interacting with a variety of knowledge bases (SQLAlchemy models,
Resource Connectors, Caches, Message Queues, etc), and can easily monitor and
process incoming data.  One could then easily build state-machines, inference
engines, or even forward/backward-chaning rule-driven expert systems.

Moksha also provides a simple yet powerful API for creating
:doc:`Producers`.  With these, developers can script
periodic tasks such as fetching data, polling resources,
warming caches, sending notifications, analyzing databases, etc.  For example,
Moksha provides a :doc:`FeedStream`, that automatically handles fetching,
parsing, caching, and sending notifications for all known feeds at a regular
interval.

These are loaded by :doc:`MokshaHub`, and are executed outside of the WSGI
application stack, but they are still able to access the Database, Cache,
MessageHub, etc.

.. seealso::

   :doc:`MokshaHub`

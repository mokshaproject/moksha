The technology that powers Moksha
=================================

Python
------
An high-level interpreted, interactive, object-oriented programming language.

`Twisted <http://twistedmatrix.com>`_
-------------------------------------

Twisted is an event-driven networking engine written in Python.  It is the core engine for the :doc:`MokshaHub`, which reacts to incoming messages (:doc:`Consumers`), runs our :doc:`Producers`, and drives the :doc:`WebSocket` Server (if it is enabled).

`ToscaWidgets2 <http://toscawidgets.org>`_
------------------------------------------

The powerful API for creating reusable "Widgets", which are essentially just
bundles of HTML, JavaScript, CSS, and render-time logic.  ToscaWidgets2 also
provides a piece of WSGI middleware that handles intelligent resource
inejection.

Templating language of your choice
----------------------------------

We prefer `Mako <http://www.makotemplates.org/>`_ first and
`Genshi <http://genshi.edgewall.org/>`_ second,
powerful templating languages that can be used for widgets or other
applications.  Other templating languages are possible.

`jQuery <http://jquery.com>`_
-----------------------------

jQuery is a fast and concise JavaScript Library that simplifies HTML document
traversing, event handling, animating, and Ajax interactions for rapid web
development. jQuery is designed to change the way that you write JavaScript.

`Orbited <http://orbited.org>`_
-------------------------------

Real-time communication for the web browser.  Orbited provides a pure
JavaScript/HTML socket in the browser.  It is a web router and firewall that
allows you to integrate web applications with arbitrary back-end systems.

`js.io <http://js.io>`_
-----------------------

Simplifies creating rich web applications by providing direct integration with
open protocols.

`AMQP <http://amqp.org/>`_/`Qpid <http://incubator.apache.org/qpid/>`_
-----------------------------------------------------------------------

`AMQP <http://amqp.org/>`_ is an open Internet Protocol for Business Messaging.
`Qpid <http://incubator.apache.org/qpid/>`_ is a message broker daemon that
receives, stores, and routes messages using the AMQP protocol.

`0mq <http://www.zeromq.org/>`_
-------------------------------

`0mq <http://www.zeromq.org/>`_ is a socket library that acts as a concurrency
framework.  Think `"spicy sockets on steroids"`.  It is one the pluggable
messaging backends for the :doc:`MokshaHub` alongside AMQP and STOMP.


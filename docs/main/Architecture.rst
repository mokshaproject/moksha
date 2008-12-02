Architecture Goals
==================

- `WSGI <http://wsgi.org>`_ (`PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_) compliant application and `middleware <http://www.wsgi.org/wsgi/Middleware_and_Utilities>`_ stack
- A real-time messaging hub using the `Advanced Message Queuing Protocol (AMQP) <http://http://amqp.org/>`_
- Highly-scalable `Orbited <http://orbited.org>`_ servers for asynchronous real-time web-browser<->server communication
- A powerful widget creation API that trivializes the creation of modular, scalable, reusable real-time widgets that can efficiently acquire data from a variety of sources.
- A data aggregation layer that handles fetching feeds for the widgets, caching
  them, and sending them to Orbited, and via AMQP messages.

===========
Scalability
===========

The architecture is designed to make it extremely scalable yet
dead-simple to hack on.  This means that you could potentially run the entire
platform on your laptop, or within a cloud.

The following architecture components can be made redundant to scale in a
production environment:

- WSGI frontends
- Orbited proxies
- AMQP message brokers
- 0mq message fabric
- Moksha hub (Feed fetchers / Data pollers / AMQP hooks & triggers / WebSocket
  Server)
- memcached daemons
- Databases

==========
Deployment
==========

Installing and configuring the Moksha mod_wsgi environment
----------------------------------------------------------

:doc:`RPMInstallation`

Serving ToscaWidgets static resources
-------------------------------------

`Deploying projects which use ToscaWidgets <http://toscawidgets.org/documentation/ToscaWidgets/deploy.html>`_

Once extracted, comment out the ToscaWidgets alias in your
`/etc/httpd/conf.d/moksha.conf`.


Setting up an AMQP message broker
---------------------------------

In production you can easily switch to an enterprise-grade message broker, such
as `Apache Qpid <http://qpid.apache.org>`_.

See the documentation on :doc:`MessageBrokers` for details on how to hook up an AMQP broker.

.. seealso::

   If you're interested in using RabbitMQ with Moksha, see the :doc:`RabbitMQ`
   docs.  Warning: it's not very well tested or supported, yet.

Setting up memcached
--------------------

After installing memcached, you'll want to update your `production.ini` configuration
to utlize the memcached Beaker extension.  This example uses two memcached servers.

.. code-block:: ini

   beaker.cache.type = ext:memcached
   beaker.cache.url = memcached1;memcached2

.. seealso::

   `Caching with TurboGears <http://turbogears.org/2.1/docs/main/Caching.html>`

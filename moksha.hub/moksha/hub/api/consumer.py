# This file is part of Moksha.
# Copyright (C) 2008-2014  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:mod:`moksha.hub.api.consumer` - The Moksha Consumer API
========================================================
Moksha provides a simple API for creating "consumers" of message topics.

This means that your consumer is instantiated when the MokshaHub is initially
loaded, and receives each message for the specified topic through the
:meth:`Consumer.consume` method.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. moduleauthor:: Ralph Bean <rbean@redhat.com>
"""

import json
import threading
import time
import logging
log = logging.getLogger('moksha.hub')

try:
    import queue  # py3
except ImportError:
    import Queue as queue  # py2

from kitchen.iterutils import iterate
from moksha.common.lib.helpers import create_app_engine
import moksha.hub.reactor


class Consumer(object):
    """ A message consumer """
    topic = ''

    # Automatically decode JSON data
    jsonify = True

    # Internal use only
    _initialized = False
    _exception_count = 0

    def __init__(self, hub):
        self.hub = hub
        self.log = log

        # Set up a queue to communicate between the main twisted thread
        # receiving raw messages, and a worker thread that pulls items off
        # the queue to do "consume" work.
        self.incoming = queue.Queue()
        self.headcount_in = self.headcount_out = 0
        self._times = []

        callback = self._consume
        if self.jsonify:
            callback = self._consume_json

        for topic in iterate(self.topic):
            log.debug('Subscribing to consumer topic %s' % topic)
            self.hub.subscribe(topic, callback)

        # If the consumer specifies an 'app', then setup `self.engine` to
        # be a SQLAlchemy engine, along with a configured DBSession
        app = getattr(self, 'app', None)
        self.engine = self.DBSession = None
        if app:
            log.debug("Setting up individual engine for consumer")
            from sqlalchemy.orm import sessionmaker
            self.engine = create_app_engine(app, hub.config)
            self.DBSession = sessionmaker(bind=self.engine)()

        self.N = int(self.hub.config.get('moksha.workers_per_consumer', 1))
        for i in range(self.N):
            moksha.hub.reactor.reactor.callInThread(self._work)

        self._initialized = True

    def __json__(self):
        if self._initialized:
            backlog = self.incoming.qsize()
            headcount_out = self.headcount_out
            headcount_in = self.headcount_in
            times = self._times
        else:
            backlog = None
            headcount_out = headcount_in = 0
            times = []

        results = {
            "name": type(self).__name__,
            "module": type(self).__module__,
            "topic": self.topic,
            "initialized": self._initialized,
            "exceptions": self._exception_count,
            "jsonify": self.jsonify,
            "backlog": backlog,
            "headcount_out": headcount_out,
            "headcount_in": headcount_in,
            "times": times,
        }
        # Reset these counters before returning.
        self.headcount_out = self.headcount_in = 0
        self._exception_count = 0
        self._times = []
        return results

    def debug(self, message):
        idx = threading.current_thread().ident
        log.debug("%r thread %r | %s" % (type(self).__name__, idx, message))

    def _consume_json(self, message):
        """ Convert our AMQP messages into a consistent dictionary format.

        This method exists because our STOMP & AMQP message brokers consume
        messages in different formats.  This causes our messaging abstraction
        to leak into the consumers themselves.

        :Note: We do not pass the message headers to the consumer (in this AMQP consumer)
        because the current AMQP.js bindings do not allow the client to change them.
        Thus, we need to throw any topic/queue details into the JSON body itself.
        """
        try:
            body = json.loads(message.body)
        except:
            log.debug("Unable to decode message body to JSON: %r" % message.body)
            body = message.body
        topic = None

        # Try some stuff for AMQP:
        try:
            topic = message.headers[0].routing_key
        except TypeError:
            # We didn't get a JSON dictionary
            pass
        except AttributeError:
            # We didn't get headers or a routing key?
            pass

        # If that didn't work, it might be zeromq
        if not topic:
            try:
                topic = message.topic
            except AttributeError:
                # Weird.  I have no idea...
                pass

        message_as_dict = {'body': body, 'topic': topic}
        self._consume(message_as_dict)

    def _consume(self, message):
        self.headcount_in += 1
        self.incoming.put(message)

    def _work(self):
        while True:
            # This is a blocking call.  It waits until a message is available.
            message = self.incoming.get()
            self.headcount_out += 1
            start = time.time()

            # Then we are being asked to quit
            if message is StopIteration:
                break

            self.debug("Worker thread picking a message.")
            try:
                self.validate(message)
            except Exception as e:
                log.warn("Received invalid message %r" % e)
                continue

            try:
                self.pre_consume(message)
            except Exception as e:
                self.log.exception(message)

            try:
                self.consume(message)
            except Exception as e:
                self.log.exception(message)
                # Keep track of how many exceptions we've hit in a row
                self._exception_count += 1

            try:
                self.post_consume(message)
            except Exception as e:
                self.log.exception(message)

            # Record how long it took to process this message (for stats)
            self._times.append(time.time() - start)

            self.debug("Going back to waiting on the incoming queue.")

        self.debug("Worker thread exiting.")

    def validate(self, message):
        """ Override to implement your own validation scheme. """
        pass

    def pre_consume(self, message):
        pass

    def consume(self, message):
        raise NotImplementedError

    def post_consume(self, message):
        pass

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message)
        except Exception as e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        for i in range(getattr(self, 'N', 0)):
            self.incoming.put(StopIteration)

        if hasattr(self, 'hub'):
            self.hub.close()

        if getattr(self, 'DBSession', None):
            self.DBSession.close()

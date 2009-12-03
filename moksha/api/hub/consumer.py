# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
:mod:`moksha.api.hub.consumer` - The Moksha Consumer API
========================================================
Moksha provides a simple API for creating "consumers" of message topics.

This means that your consumer is instantiated when the MokshaHub is initially
loaded, and receives each message for the specified topic through the
:meth:`Consumer.consume` method.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import logging
log = logging.getLogger('moksha.hub')

from moksha.hub.hub import MokshaHub
from moksha.lib.helpers import listify, create_app_engine, json
from sqlalchemy.orm import sessionmaker

class Consumer(object):
    """ A message consumer """
    topic = None

    # Automatically decode JSON data
    jsonify = True

    def __init__(self):
        self.hub = MokshaHub()
        self.log = log
        if self.hub.amqp_broker and not self.hub.stomp_broker:
            for topic in listify(self.topic):
                log.debug('Subscribing to consumer topic %s' % topic)
                server_queue_name = 'moksha_consumer_' + self.hub.session.name
                self.hub.queue_declare(queue=server_queue_name, exclusive=True)
                self.hub.exchange_bind(server_queue_name, binding_key=topic)
                local_queue_name = 'moksha_consumer_' + self.hub.session.name
                self.hub.local_queue = self.hub.session.incoming(local_queue_name)
                self.hub.message_subscribe(queue=server_queue_name,
                                       destination=local_queue_name)
                self.hub.local_queue.start()
                if self.jsonify:
                    self.hub.local_queue.listen(self._consume_json)
                else:
                    self.hub.local_queue.listen(self._consume)

        # If the consumer specifies an 'app', then setup `self.engine` to
        # be a SQLAlchemy engine, along with a configured DBSession
        app = getattr(self, 'app', None)
        self.engine = self.DBSession = None
        if app:
            log.debug("Setting up individual engine for consumer")
            self.engine = create_app_engine(app)
            self.DBSession = sessionmaker(bind=self.engine)()

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
            body = json.decode(message.body)
        except:
            log.debug("Unable to decode message body to JSON: %r" % message.body)
            body = message.body
        topic = None
        try:
            topic = message.headers[0].routing_key
        except TypeError:
            # We didn't get a JSON dictionary
            pass
        except AttributeError:
            # We didn't get headers or a routing key?
            pass

        self.consume({'body': body, 'topic': topic})

    def _consume(self, message):
        self.consume(message)

    def consume(self, message):
        raise NotImplementedError

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message, jsonify=self.jsonify)
        except Exception, e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        self.hub.close()
        if self.DBSession:
            self.DBSession.close()

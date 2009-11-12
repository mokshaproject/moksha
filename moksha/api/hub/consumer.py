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
from moksha.lib.helpers import listify, create_app_engine

class Consumer(object):
    """ A message consumer """
    topic = None

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
                self.hub.local_queue.listen(self.consume)

        # If the consumer specifies an 'app', then setup `self.engine` to
        # be a SQLAlchemy engine, along with a configured DBSession
        app = getattr(self, 'app', None)
        if app:
            from moksha.model import DBSession
            self.engine = create_app_engine(app)
            DBSession.configure(bind=self.engine)

    def consume(self, message):
        raise NotImplementedError

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message)
        except Exception, e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        self.hub.close()

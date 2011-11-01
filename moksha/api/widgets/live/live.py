# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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
#
# Authors: Luke Macken <lmacken@redhat.com>
#          Ralph Bean <ralph.bean@gmail.com>

from tg import config
from paste.deploy.converters import asbool

import moksha
import moksha.utils

from uuid import uuid4

from tw.api import Widget

from moksha.exc import MokshaException
from moksha.api.widgets.stomp import (
    StompWidget, stomp_subscribe, stomp_unsubscribe)
from moksha.api.widgets.amqp import (
    AMQPSocket, amqp_subscribe, amqp_unsubscribe)

import tw2.core.params as pm
import tw2.core.widgets

class TW2LiveWidgetMeta(tw2.core.widgets.WidgetMeta):
    pass

class TW2LiveWidget(tw2.core.Widget):
    """ A live streaming widget based on toscawidgets2

    This widget handles automatically subscribing your widget to any given
    topics, and registers all of the stomp callbacks.

    The basics of the LiveWidget::

        class MyLiveWidget(LiveWidget):
            topic = 'mytopic'
            onmessage = 'console.log(json)'
            template = 'mako:myproject.templates.mylivewidget'
    """
    __metaclass__ = TW2LiveWidgetMeta

    backend = pm.Param(
        'moksha livesocket backend to use',
        default=config.get('moksha.livesocket.backend', 'stomp').lower())
    topic = pm.Param('Topic to which this widget is subscribed')
    onmessage = pm.Param('js to execute on message received', default=None)

    def prepare(self):
        """ Get this widget ready for display

        Register this widget's message topic callbacks
        """
        if not hasattr(self, 'id'):
            self.id = str(uuid4())
            self.compound_id = self.id

        if not self.onmessage:
            raise MokshaException('%s must be provided an onmessage callback' %
                                  self.__class__.__name__)

        super(TW2LiveWidget, self).prepare()

        if not self.topic:
            raise MokshaException('You must specify a `topic` to subscribe to')

        self.topic = isinstance(self.topic, list) and self.topic or [self.topic]

        backend_lookup = {
            'stomp': StompWidget.callbacks,
            'amqp': AMQPSocket.callbacks,
        }
        callbacks = backend_lookup[self.backend]

        for callback in callbacks:
            if callback == 'onmessageframe':
                for topic in self.topic:
                    cb = getattr(self, 'onmessage').replace('${id}', self.id)
                    moksha.utils.livewidgets[callback][topic].append(cb)
            elif callback == 'onconnectedframe':
                moksha.utils.livewidgets[callback].append(subscribe_topics(self.topic))
            elif getattr(self, callback, None):
                moksha.utils.livewidgets[callback].append(getattr(self, callback))

    @classmethod
    def get_topics(cls):
        topics = []
        for key in ('topic', 'topics'):
            if hasattr(cls, key):
                topic = getattr(cls, key)
                if topic:
                    if isinstance(topic, basestring):
                        map(topics.append, topic.split())
                    else:
                        topics += topic
        return topics

    @classmethod
    def subscribe_topics(cls, topics):
        backend = config.get('moksha.livesocket.backend', 'stomp').lower()
        backend_lookup = {
            'stomp': stomp_subscribe,
            'amqp': amqp_subscribe,
        }
        try:
            return backend_lookup[backend](topics)
        except KeyError:
            raise MokshaException("Unknown `moksha.livesocket.backend` %r. "
                                  "Valid backends are currently 'amqp' and "
                                  "'stomp'." % backend)

    @classmethod
    def unsubscribe_topics(cls, topics):
        backend = config.get('moksha.livesocket.backend', 'stomp').lower()
        backend_lookup = {
            'stomp': stomp_unsubscribe,
            'amqp': amqp_unsubscribe,
        }
        try:
            return backend_lookup[backend](topics)
        except KeyError:
            raise MokshaException("Unknown `moksha.livesocket.backend` %r. "
                                  "Valid backends are currently 'amqp' and "
                                  "'stomp'." % backend)


class TW1LiveWidget(Widget):
    """ A live streaming widget.

    This widget handles automatically subscribing your widget to any given
    topics, and registers all of the stomp callbacks.

    The basics of the LiveWidget::

        class MyLiveWidget(LiveWidget):
            topic = 'mytopic'
            onmessage = 'console.log(json)'
            template = 'mako:myproject.templates.mylivewidget'

    """
    engine_name = 'mako'

    def __init__(self, id, *args, **kw):
        super(LiveWidget, self).__init__(*args, **kw)
        self.backend = config.get('moksha.livesocket.backend', 'stomp').lower()

    def update_params(self, d):
        """ Register this widgets message topic callbacks """
        super(LiveWidget, self).update_params(d)
        topics = d.get('topic', getattr(self, 'topic', d.get('topics',
                getattr(self, 'topics', None))))
        if not topics:
            raise MokshaException('You must specify a `topic` to subscribe to')
        topics = isinstance(topics, list) and topics or [topics]
        callbacks = []
        if self.backend == 'stomp':
            callbacks = StompWidget.callbacks
        elif self.backend == 'amqp':
            callbacks = AMQPSocket.callbacks
        for callback in callbacks:
            if callback == 'onmessageframe':
                for topic in topics:
                    cb = getattr(self, 'onmessage').replace('${id}', self.id)
                    moksha.utils.livewidgets[callback][topic].append(cb)
            elif callback == 'onconnectedframe':
                moksha.utils.livewidgets['onconnectedframe'].append(
                        subscribe_topics(topics))
            elif callback in self.params:
                moksha.utils.livewidgets[callback].append(getattr(self, callback))

    def get_topics(self):
        topics = []
        for key in ('topic', 'topics'):
            if hasattr(self, key):
                topic = getattr(self, key)
                if topic:
                    if isinstance(topic, basestring):
                        map(topics.append, topic.split())
                    else:
                        topics += topic
        return topics

    @classmethod
    def subscribe_topics(cls, topics):
        backend = config.get('moksha.livesocket.backend', 'stomp').lower()
        if backend == 'amqp':
            return amqp_subscribe(topics)
        elif backend == 'stomp':
            return stomp_subscribe(topics)
        else:
            raise MokshaException("Unknown `moksha.livesocket.backend` %r. "
                                  "Valid backends are currently 'amqp' and "
                                  "'stomp'." % backend)

    @classmethod
    def unsubscribe_topics(cls, topics):
        backend = config.get('moksha.livesocket.backend', 'stomp').lower()
        if backend == 'amqp':
            return amqp_unsubscribe(topics)
        elif backend == 'stomp':
            return stomp_unsubscribe(topics)
        else:
            raise MokshaException("Unknown `moksha.livesocket.backend` %r. "
                                  "Valid backends are currently 'amqp' and "
                                  "'stomp'." % backend)


if asbool(config.get('moksha.use_tw2', False)):
    LiveWidget = TW2LiveWidget
    LiveWidgetMeta = TW2LiveWidgetMeta
else:
    LiveWidget = TW1LiveWidget
    LiveWidgetMeta = None

# Moksha Topic subscription handling methods
subscribe_topics = LiveWidget.subscribe_topics
unsubscribe_topics = LiveWidget.unsubscribe_topics

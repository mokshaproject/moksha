# This file is part of Moksha.
# Copyright (C) 2018  Red Hat, Inc.
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
# Authors: Paul Belanger <pabelanger@redhat.com>

import logging

import paho.mqtt.publish as publish

from moksha.hub.messaging import MessagingHubExtension

log = logging.getLogger('moksha.hub')


class MqttHubExtension(MessagingHubExtension):

    def __init__(self, hub, config):
        self.hostname = config.get('mqtt_hostname', 'localhost')
        self.port = config.get('mqtt_port', 1883)
        self.client_id = config.get('mqtt_client_id', None)
        self.keepalive = config.get('mqtt_keepalive', 60)
        self.qos = config.get('mqtt_qos', 0)

        self.auth = None
        username = config.get('mqtt_username', None)
        if username:
            self.auth = {
                'username': username
            }
            self.auth['password'] = config.get('mqtt_password', None)

        self.tls = None
        ca_certs = config.get('mqtt_ca_certs', None)
        if ca_certs:
            self.tls = {
                'ca_certs': ca_certs
            }
            self.tls['certfile'] = config.get('mqtt_certfile', None)
            self.tls['keyfile'] = config.get('mqtt_keyfile', None)

        super(MqttHubExtension, self).__init__()

    def send_message(self, topic, message, **headers):
        publish.single(topic, message, hostname=self.hostname,
                       port=self.port, client_id=self.client_id,
                       keepalive=self.keepalive, auth=self.auth,
                       tls=self.tls, qos=self.qos)

        super(MqttHubExtension, self).send_message(topic, message, **headers)

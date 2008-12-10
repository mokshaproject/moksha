# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

"""
The Moksha Real-time Hub
"""

from tw.api import Widget, JSLink, js_callback, js_function

# @@ Make the orbited url globally configurable
ORBITED_URL = 'http://localhost:9000'
orbited_js = JSLink(link=ORBITED_URL + '/static/Orbited.js')

class OrbitedWidget(Widget):
    params = {
        'onopen': 'A javascript callback for when the connection opens',
        'onread': 'A javascript callback for when new data is read',
        'onclose': 'A javascript callback for when the connection closes',
    }
    onopen = onread = onclose = js_callback('function(){}')
    javascript = [orbited_js]
    template = """
        <script type="text/javascript">
            Orbited.settings.port = 9000
            Orbited.settings.hostname = 'localhost'
            document.domain = document.domain
            TCPSocket = Orbited.TCPSocket
            connect = function() {
                conn = new TCPSocket()
                conn.onread = ${onread}
                conn.onopen = ${onopen}
                conn.onclose = ${onclose}
                conn.open('localhost', 9000)
            }
            $(document).ready(function() {
                connect()
            })
        </script>
    """

################################################################################

import qpid
from qpid.client import Client

AMQP_SPEC = '/usr/share/amqp/amqp.0-10.xml'
QPID_HOST = '127.0.0.1'
QPID_PORT = 5672
QPID_USER = 'guest'
QPID_PASSWORD = 'guest'

class MokshaHub(object):

    client = None # qpid client
    session = None # qpid client session

    def __init__(self):
        self.init_qpid_client()
        self.init_qpid_session()

    def init_qpid_client(self):
        self.client = Client(QPID_HOST, QPID_PORT, qpid.spec.load(AMQP_SPEC))
        self.client.start()
        #self.client.start({'LOGIN': QPID_USER, 'PASSWORD': QPID_PASSWORD})

    def init_qpid_client_session(self):
        self.session = self.client.session()
        self.session.session_open()

    def close_session(self):
        self.session.session_close()

    def create_queue(self, queue, routing_key, exchange='amq.direct'):
        self.session.queue_declare(queue=queue)
        self.session.queue_bind(exchange=exchange, queue=queue,
                                routing_key=routing_key)

    def send_message(self, routing_key, message):
        raise NotImplementedError

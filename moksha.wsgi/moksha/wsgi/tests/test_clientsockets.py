import webtest

import moksha.common.testtools.utils as testutils

from moksha.wsgi.widgets.api.live import get_moksha_socket
from moksha.wsgi.middleware import make_moksha_middleware
from tw2.core import make_middleware as make_tw2_middleware


class TestClientSocketDumb:
    def _setUp(self):
        def kernel(config):
            def app(environ, start_response):
                start_response('200 OK', [('Content-Type', 'text/html')])
                socket = get_moksha_socket(config)
                return map(str, [socket.display()])

            app = make_moksha_middleware(app, config)
            app = make_tw2_middleware(app, config)
            app = webtest.TestApp(app)
            self.app = app

        for _setup, name in testutils.make_setup_functions(kernel):
            yield _setup, name

    def _tearDown(self):
        pass

    @testutils.crosstest
    def test_has_socket_str(self):
        targets = ['moksha_websocket', 'TCPSocket']
        response = self.app.get('/')
        assert(any([target in response for target in targets]))

import webtest

import moksha.common.testtools.utils as testutils

import moksha.wsgi.widgets.api.live

from moksha.wsgi.middleware import make_moksha_middleware
from tw2.core import make_middleware as make_tw2_middleware


class TestLiveWidget:
    def _setUp(self):
        def kernel(config):
            def app(environ, start_response):
                start_response('200 OK', [('Content-Type', 'text/html')])
                class MyWidget(moksha.wsgi.widgets.api.live.LiveWidget):
                    template = "moksha.wsgi.tests.templates.empty"

                    onmessage = 'console.log(json)'
                    topic = 'test'

                    backend = config['moksha.livesocket.backend']

                return map(str, [MyWidget.display()])

            app = make_moksha_middleware(app, config)
            app = make_tw2_middleware(app, config)
            app = webtest.TestApp(app)
            self.app = app

        for _setup, name in testutils.make_setup_functions(kernel):
            yield _setup, name

    def _tearDown(self):
        pass

    @testutils.crosstest
    def test_can_render(self):
        response = self.app.get('/')

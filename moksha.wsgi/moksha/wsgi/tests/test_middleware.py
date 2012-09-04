import unittest
import moksha.wsgi.middleware
import webtest

from nose.tools import raises
from nose.tools import eq_


class TestMiddleware(unittest.TestCase):
    def setUp(self):
        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['Hello, world!\n']

        self.app = app

    def test_middleware_wrap(self):
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, {})

    def test_middleware_simple(self):
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, {})
        test_app = webtest.TestApp(app)
        response = test_app.get('/')
        eq_(response.status, '200 OK')

    @raises(KeyError)
    def test_no_registry(self):
        config = {'moksha.registry': False}
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, config)
        response = webtest.TestApp(app).get('/')

    def test_external_registry(self):
        config = {'moksha.registry': False}
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, config)
        from paste.registry import RegistryManager
        app = RegistryManager(app)
        response = webtest.TestApp(app).get('/')
        eq_(response.status, '200 OK')

    @raises(NotImplementedError)
    def test_connectors(self):
        config = {'moksha.connectors': True}
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, config)
        response = webtest.TestApp(app).get('/')

    @raises(NotImplementedError)
    def test_csrf(self):
        config = {'moksha.csrf_protection': True}
        app = moksha.wsgi.middleware.make_moksha_middleware(self.app, config)
        response = webtest.TestApp(app).get('/')

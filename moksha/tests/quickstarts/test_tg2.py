import os
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp

class TestTG2AppInMoksha(object):

    def setUp(self):
        tg2app_path = os.path.join(os.path.dirname(__file__), 'tg2app')
        pkg_resources.working_set.add_entry(tg2app_path)
        self.app = loadapp('config:/srv/moksha/development.ini',
                           relative_to=tg2app_path)
        self.app = TestApp(self.app)

    def test_index(self):
        """ Ensure we can still get to the Moksha index page """
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def test_tg2app_controller(self):
        """ Test grabbing the index of our TG2 app """
        resp = self.app.get('/apps/tg2app')
        assert 'Now Viewing: index' in resp

    def test_tg2app_model(self):
        """ Test creating a new user with the apps model """
        from tg2app.model import User, DBSession
        me = User()
        me.user_name = u'jim'
        me.email_address = u'jim@bob.com'
        DBSession.add(me)
        DBSession.flush()
        assert DBSession.query(User).count() == 1

    def test_tg2app_wsgi(self):
        """ Ensure we can get to TG2 when it is mounted as a WSGI app """
        resp = self.app.get('/apps/tg2wsgi/')
        assert 'Now Viewing: index' in resp


class TestTG2App(object):
    """ Test mounting the TurboGears2 app directly.

    Since this test app does not contain the MokshaMiddleware, it
    won't do much, but we should still make sure we can use it.

    """
    def setUp(self):
        tg2app_path = os.path.join(os.path.dirname(__file__), 'tg2app')
        cfg = os.path.join(tg2app_path, 'development.ini')
        pkg_resources.working_set.add_entry(tg2app_path)
        self.app = loadapp('config:' + cfg,
                           relative_to=tg2app_path)
        self.app = TestApp(self.app)

    def test_index(self):
        """ Make sure we properly route to the root of the TG2 app """
        resp = self.app.get('/')
        assert 'Welcome to TurboGears 2.0' in resp

import os
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp

class TestTG2App(object):

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

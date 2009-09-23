import os
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp

class TestTG2App(object):

    def setUp(self):
        tg2app_path = os.path.join(os.path.dirname(__file__), 'tg2app')
        pkg_resources.working_set.add_entry(tg2app_path)
        reload(pkg_resources)
        self.app = loadapp('config:/srv/moksha/development.ini',
                           relative_to=tg2app_path)
        self.app = TestApp(self.app)

    def test_index(self):
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def test_tg2app_controller(self):
        resp = self.app.get('/apps/tg2app')
        assert 'Now Viewing: index' in resp

    def test_tg2app_model(self):
        from tg2app.model import User, DBSession
        me = User()
        me.user_name = u'jim'
        me.email_address = u'jim@bob.com'
        DBSession.add(me)
        DBSession.flush()
        assert DBSession.query(User).count() == 1

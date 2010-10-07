import os
import pylons
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp
from moksha.lib.helpers import get_moksha_dev_config

class TestTG2AppInMoksha(object):

    def setUp(self):
        tg2app_path = os.path.join(os.path.dirname(__file__), 'tg2app')
        pkg_resources.working_set.add_entry(tg2app_path)
        self.app = loadapp('config:%s' % get_moksha_dev_config(),
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

    #def test_tg2app_wsgi(self):
    #    """
    #    Test plugging a TurboGears2/Pylons app into moksha via the
    #    moksha.wsgiapp extension-point.

    #    :Note: This is a bad idea, as the the TG2 app will stomp on Moksha's
    #    pylons.config, since Moksha is a TG2 app as well.  So, this test
    #    will verify that they don't play well together.
    #    """
    #    # The tg2app will stomp on the pylons.paths and TG will dispatch
    #    # to the plugins RootController, instead of Moksha's
    #    resp = self.app.get('/apps/tg2wsgi/')
    #    assert '[ Moksha ]' in resp
    #    # It's getting to the app
    #    #assert 'Welcome to TurboGears' in resp, resp

    #    #import tg2app
    #    #assert pylons.config['package'] == tg2app, pylons.config['package']


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

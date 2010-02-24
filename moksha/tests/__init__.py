# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
"""Unit and functional test suite for Moksha """

from os import path
import sys

from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes import url_for
from webtest import TestApp
from nose.tools import eq_

from moksha import model

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']

def setup_db():
    engine = config['pylons.app_globals'].sa_engine 
    model.init_model(engine)
    model.metadata.create_all(engine)

def teardown_db():
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)

def setup_app(application): 
    # Loading the application:
    conf_dir = config.here
    wsgiapp = loadapp('config:test.ini#%s' % application,
                      relative_to=conf_dir)
    app = TestApp(wsgiapp)
    # Setting it up:
    test_file = path.join(conf_dir, 'test.ini')
    cmd = SetupCommand('setup-app')
    cmd.run([test_file])
    return app

__all__ = ['url_for', 'TestController']


class TestController(object):
    """
    Base functional test case for the controllers.

    The Moksha application instance (``self.app``) set up in this test 
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check Moksha for the repoze.who integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """

    application_under_test = 'main_without_authn'

    def setUp(self):
        # Loading the application:
        conf_dir = config.here
        wsgiapp = loadapp('config:test.ini#%s' % self.application_under_test,
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        # Setting it up:
        test_file = path.join(conf_dir, 'test.ini')
        cmd = SetupCommand('setup-app')
        cmd.run([test_file])

    def tearDown(self):
        # Cleaning up the database:
        engine = config['pylons.app_globals'].sa_engine
        model.metadata.drop_all(engine)

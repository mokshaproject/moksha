# -*- coding: utf-8 -*-
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

"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true

from moksha.tests import TestController

class TestRootController(TestController):

    def test_index(self):
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def test_jquery_injection(self):
        """ Ensure jQuery is getting injected on our main dashboard """
        resp = self.app.get('/')
        assert 'jquery' in resp

    def test_global_resources(self):
        """ Ensure we are getting our global resources injected """
        resp = self.app.get('/')
        assert 'moksha_csrf_token' in resp

    # Disabled, since we don't want to ship the menu by default
    #def test_menu(self):
    #    """ Ensure that our default menu is being created """
    #    resp = self.app.get('/')
    #    assert 'buildMenu' in resp

    def test_tcpsocket(self):
        """ Ensure our TCP socket is getting injected """
        resp = self.app.get('/')
        assert 'TCPSocket' in resp or 'moksha_amqp_conn' in resp

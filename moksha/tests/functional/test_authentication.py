# -*- coding: utf-8 -*-
# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Integration tests for the :mod:`repoze.who`-powered authentication sub-system.

As Moksah grows and the authentication method changes, only these tests
should be updated.

"""

from moksha.tests import TestController


class TestAuthentication(TestController):
    """
    Tests for the default authentication setup.

    By default in TurboGears 2, :mod:`repoze.who` is configured with the same
    plugins specified by repoze.what-quickstart (which are listed in
    http://code.gustavonarea.net/repoze.what-quickstart/#repoze.what.plugins.quickstart.setup_sql_auth).

    As the settings for those plugins change, or the plugins are replaced,
    these tests should be updated.

    """

    application_under_test = 'main'

    def test_forced_login(self):
        """
        Anonymous users must be redirected to the login form when authorization
        is denied.

        Next, upon successful login they should be redirected to the initially
        requested page.

        """
        # Requesting a protected area
        resp = self.app.get('/moksha_admin/', status=302)
        assert resp.location.startswith('http://localhost/login') or \
               resp.location.startswith('/login')
        # Getting the login form:
        resp = resp.follow(status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = u'manager'
        form['password'] = u'managepass'
        post_login = form.submit(status=302)
        # Being redirected to the initially requested page:
        assert post_login.location.startswith('http://localhost/post_login') or \
               post_login.location.startswith('/post_login')
        initial_page = post_login.follow(status=302)
        assert 'authtkt' in initial_page.request.cookies, \
               "Session cookie wasn't defined: %s" % initial_page.request.cookies
        assert initial_page.location.startswith('http://localhost/moksha_admin/'), \
               initial_page.location

    def test_voluntary_login(self):
        """Voluntary logins must work correctly"""
        # Going to the login form voluntarily:
        resp = self.app.get('/login', status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = u'manager'
        form['password'] = 'managepass'
        post_login = form.submit(status=302)
        # Being redirected to the home page:
        assert post_login.location.startswith('http://localhost/post_login') or\
               post_login.location.startswith('/post_login')
        home_page = post_login.follow(status=302)
        assert 'authtkt' in home_page.request.cookies, \
               'Session cookie was not defined: %s' % home_page.request.cookies
        assert home_page.location.startswith('http://localhost/')

    def test_logout(self):
        """Logouts must work correctly"""
        # Logging in voluntarily the quick way:
        resp = self.app.get('/login_handler?login=manager&password=managepass',
                            status=302)
        resp = resp.follow(status=302)
        assert 'authtkt' in resp.request.cookies, \
               'Session cookie was not defined: %s' % resp.request.cookies
        # Logging out:
        resp = self.app.get('/logout_handler', status=302)
        assert resp.location.startswith('http://localhost/post_logout') or \
               resp.location.startswith('/post_logout')
        # Finally, redirected to the home page:
        home_page = resp.follow(status=302)
        authtkt = home_page.request.cookies.get('authtkt')
        assert authtkt in ('', 'INVALID'), \
               'Session cookie was not deleted: %s' % home_page.request.cookies
        assert home_page.location == 'http://localhost/', repr(home_page.location)

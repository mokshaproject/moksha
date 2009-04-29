# -*- coding: utf-8 -*-
# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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
        assert resp.location.startswith('http://localhost/login')
        # Getting the login form:
        resp = resp.follow(status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = u'manager'
        form['password'] = 'managepass'
        post_login = form.submit(status=302)
        # Being redirected to the initially requested page:
        assert post_login.location.startswith('http://localhost/post_login')
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
        assert post_login.location.startswith('http://localhost/post_login'), post_login.location
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
        assert resp.location.startswith('http://localhost/post_logout')
        # Finally, redirected to the home page:
        home_page = resp.follow(status=302)
        assert home_page.request.cookies.get('authtkt') == '', \
               'Session cookie was not deleted: %s' % home_page.request.cookies
        assert home_page.location == 'http://localhost/', home_page.location

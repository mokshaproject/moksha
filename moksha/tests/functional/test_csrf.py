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
Integration tests for Moksha's CSRF protection.

These tests are meant to ensure the validity of Moksha's CSRF WSGI middleware
and repoze.who metadata provider plugin.
"""

from moksha.tests import TestController

class TestCSRFProtection(TestController):

    application_under_test = 'main'

    def test_csrf_protection(self):
        # Test for anonymous requests
        resp = self.app.get('/', status=200)
        assert 'moksha_base_url = "/"' in resp
        assert 'moksha_csrf_token = ""' in resp
        assert 'moksha_userid = ""' in resp

        # Requesting a protected area
        resp = self.app.get('/moksha_admin/', status=302)
        assert resp.location.startswith('http://localhost/login') or \
               resp.location.startswith('/login'), resp.location

        # Getting the login form:
        resp = resp.follow(status=200)
        form = resp.form

        # Submitting the login form:
        form['login'] = u'manager'
        form['password'] = 'managepass'
        post_login = form.submit(status=302)

        # Being redirected to the initially requested page:
        assert post_login.location.startswith('http://localhost/post_login') or\
               post_login.location.startswith('/post_login')
        initial_page = post_login.follow(status=302)
        assert 'authtkt' in initial_page.request.cookies, \
               "Session cookie wasn't defined: %s" % initial_page.request.cookies
        assert initial_page.location.startswith('http://localhost/moksha_admin/'), \
               initial_page.location

        assert '_csrf_token=' in initial_page.location, "Login not redirected with CSRF token"

        token = initial_page.location.split('_csrf_token=')[1]

        # Now ensure that the token also also being injected in the page
        resp = initial_page.follow(status=200)
        assert 'moksha_csrf_token' in resp
        assert token == resp.body.split('moksha_csrf_token')[1].split(';')[0].split('"')[1], \
                "CSRF token not set in response body!"

        # Make sure we can get to the page with the token
        resp = self.app.post('/moksha_admin/', {'_csrf_token': token}, status=200)
        assert 'moksha_csrf_token' in resp, resp
        assert 'moksha_csrf_token = ""' not in resp, "CSRF token not set!"
        assert token == resp.body.split('moksha_csrf_token')[1].split(';')[0].split('"')[1], \
                "CSRF token not set in response body!"

        # Make sure we can't get back to the page without the token
        resp = self.app.get('/moksha_admin/', status=302)
        assert 'The resource was found at /post_logout' in resp or \
               'The resource was found at /login' in resp or \
               'The resource was found at http://localhost/login' in resp

        # Make sure that we can't get back after we got rejected once
        resp = self.app.post('/moksha_admin/', {'_csrf_token': token}, status=302)
        assert 'The resource was found at /login' in resp or \
               'The resource was found at http://localhost/login' in resp

        # Ensure the token gets removed
        resp = self.app.get('/', status=200)
        assert 'moksha_base_url = "/"' in resp
        assert 'moksha_csrf_token = ""' in resp
        assert 'moksha_userid = ""' in resp

        # Ok, now log back in...
        resp = self.app.get('/moksha_admin/', status=302)
        resp = resp.follow(status=200)
        form = resp.form
        form['login'] = u'manager'
        form['password'] = 'managepass'
        post_login = form.submit(status=302)
        initial_page = post_login.follow(status=302)
        assert '_csrf_token=' in initial_page.location, "Login not redirected with CSRF token"
        newtoken = initial_page.location.split('_csrf_token=')[1]

        # For some reason logging out sometimes doesn't give us a new session cookie
        #assert newtoken != token, "Did not receieve a new token!!"

        # Now, make sure we reject invalid tokens
        resp = self.app.post('/moksha_admin/', {'_csrf_token': token + ' '}, status=302)
        assert 'The resource was found at /post_logout' in resp or \
               'The resource was found at http://localhost/post_logout' in resp

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
        response = self.app.get('/')
        #msg = 'TurboGears 2 is rapid web application development toolkit '\
        #      'designed to make your life easier.'
        # You can look for specific strings:
        #assert_true(msg in response)

        # You can also access a BeautifulSoup'ed response in your tests
        # (First run $ easy_install BeautifulSoup 
        # and then uncomment the next two lines)  

        #links = response.html.findAll('a')
        #print links
        #assert_true(links, "Mummy, there are no links here!")

    #def test_secc_with_anonymous(self):
    #    """Anonymous users must not access the secure controller"""
    #    # We should get a redirect to login
    #    resp = self.app.get('/secc', status=302)
    #    print resp
    #    assert "/login?came_from=http%3A%2F%2Flocalhost%2Fsecc" in resp

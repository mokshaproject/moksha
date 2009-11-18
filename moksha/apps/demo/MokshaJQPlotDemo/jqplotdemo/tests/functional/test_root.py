# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true

from jqplotdemo.tests import TestController

class TestRootController(TestController):

    def test_index(self):
        """ Make sure we can get to the main jqplot demo """
        response = self.app.get('/')
        assert_true("Moksha JQPlot Demo" in response)

    def test_tcpsocket(self):
        """ Make sure the Moksha socket gets injected """
        response = self.app.get('/')
        assert_true('TCPSocket' in response or 'moksha_amqp_conn' in response)

    def test_jqplot(self):
        """ Make sure jQuery is injected properly """
        response = self.app.get('/')
        assert_true('jquery.js' in response)

    def test_jqplot(self):
        """ Make sure jqplot is injected and getting called """
        response = self.app.get('/')
        assert_true('jquery.jqplot.js' in response)
        assert_true('$.jqplot' in response)

    def test_moksha_widget(self):
        """ Make sure we can get to widgets directly through Moksha """
        try:
            response = self.app.get('/widgets/jqplot_pie_widget')
        except ValueError, e:
            assert 'JQPlotWidget must have data to graph' in e

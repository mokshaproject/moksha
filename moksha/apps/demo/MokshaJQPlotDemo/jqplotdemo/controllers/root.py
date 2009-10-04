# -*- coding: utf-8 -*-
"""Main Controller"""

from tw.api import js_function
from tg import expose, flash, require, url, request, redirect, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from moksha.lib.base import BaseController

from jqplotdemo.model import DBSession, metadata
from jqplotdemo.widgets import plot_widget, pie_widget
from jqplotdemo.controllers.error import ErrorController
from jqplotdemo.controllers.plots import AsynchronousJQPlotDemoController

class RootController(BaseController):
    """
    The root controller for the JQPlotDemo application.

    A controller supporting json service to polling widgets is mounted below.
    """

    error = ErrorController()

    plots = AsynchronousJQPlotDemoController()

    @expose('jqplotdemo.templates.index')
    def index(self):
        d = RootController.plots.index()
        plot_data, plot_options = d['data'],d['options']
        plot_options['series'] = [{'showMarker' : False}
                                  for series in plot_data]
        plot_options['title'] = 'Sine of the times'
        plot_options['axes']['xaxis']['renderer'] = \
                js_function('$.jqplot.DateAxisRenderer')
        plot_options['axes']['xaxis']['tickOptions'] = {'formatString': '%T'}

        tmpl_context.plot_widget = plot_widget

        d = RootController.plots.pie()
        pie_data, pie_options = d['data'],d['options']
        pie_options['title'] = 'Most recent value of each series'
        pie_options['seriesDefaults'] = {
            'renderer' : js_function('$.jqplot.PieRenderer'),
            'rendererOptions' : {
                'sliceMargin' : 8,
                'fill' : False,
                'lineWidth' : 5
            }
        }

        tmpl_context.pie_widget = pie_widget

        return dict(plot_data=plot_data, plot_options=plot_options,
                    pie_data=pie_data, pie_options=pie_options)

    @expose('jqplotdemo.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

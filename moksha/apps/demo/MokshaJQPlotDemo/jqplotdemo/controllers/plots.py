# -*- coding: utf-8 -*-

from time import time
from math import sin, cos
from random import random

from tg import expose
from tw.api import js_function

from jqplotdemo.lib.base import Controller

def make_data():
    """ Sin of the times! """
    now = int(time())
    n = 20.0
    series1 = [[i*1000,sin(i/n)] for i in range(now-100, now)]
    series2 = [[i*1000,abs(sin(i/n))**((i%(2*n))/n)] for i in range(now-100, now)]
    series3 = [[i*1000,cos(i/(n+1))*1.5] for i in range(now-100, now)]
    series4 = [[series2[i][0], series2[i][1] * series3[i][1]] for i in range(len(series3))]
    data = [series1, series2, series3,series4]
    return data

def find_bounds(data):
    minx = min( [min( [point[0] for point in series] ) for series in data]) 
    maxx = max( [max( [point[0] for point in series] ) for series in data]) 
    miny = min( [min( [point[1] for point in series] ) for series in data])
    maxy = max( [max( [point[1] for point in series] ) for series in data])
    miny -= 0.1
    maxy += 0.1
    return minx, maxx, miny, maxy

def get_plot_data():
    data = make_data()
    minx, maxx, miny, maxy = find_bounds(data)
    options = {
        'axes' : {
            'xaxis' : { 'min' : minx, 'max' : maxx },
            'yaxis' : { 'min' : miny, 'max' : maxy },
        }
    }
    return dict(data=data, options=options)

def get_pie_data():
    data = make_data()
    options = {}
    slices = [['series %s' % str(i), data[i][-1][1] + 1.5]
               for i in range(len(data))]
    return dict(data=[slices], options=options)


class AsynchronousJQPlotDemoController(Controller):

    @expose('json')
    def index(self):
        return dict(**get_plot_data())

    @expose('json')
    def pie(self, *args, **kw):
        return dict(**get_pie_data())

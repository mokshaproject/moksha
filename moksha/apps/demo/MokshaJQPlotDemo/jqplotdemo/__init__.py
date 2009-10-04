# -*- coding: utf-8 -*-
"""The JQPlotDemo package"""

# Severe Monkey Patching, until this patch gets accepted
# http://toscawidgets.org/trac/tw/ticket/30
from jqplotdemo import js
from tw import api
api.TWEncoder = js.TWEncoder
api.js_symbol = js.js_symbol
api.js_callback = js.js_callback
api.js_function = js.js_function
api._js_call = js._js_call

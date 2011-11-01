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

import uuid
import simplejson as json

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.forms
import tw.jquery
import tw.jquery.ui_core

import tw2.core as twc
import tw2.forms
import tw2.jquery
import tw2.jqplugins.ui

from moksha.lib.helpers import when_ready
from moksha.widgets.json import (
    tw1_jquery_json_js, tw2_jquery_json_js)
from moksha.widgets.jquery_template import (
    tw1_jquery_template_js, tw2_jquery_template_js)

tw1_moksha_ui_grid_js = tw.api.JSLink(
    filename='public/javascript/ui/moksha.ui.grid.js',
    modname='moksha',
    javascript=[tw.jquery.ui_core.jquery_ui_core_js,
                tw1_jquery_template_js,
                tw1_jquery_json_js])

tw1_moksha_ui_popup_js = tw.api.JSLink(
    filename='public/javascript/ui/moksha.ui.popup.js',
    modname='moksha',
    javascript=[tw.jquery.ui_core.jquery_ui_core_js])

tw2_moksha_ui_grid_js = twc.JSLink(
    filename='public/javascript/ui/moksha.ui.grid.js',
    modname='moksha',
    resources=[tw2.jqplugins.ui.jquery_ui_js,
               tw2_jquery_template_js,
               tw2_jquery_json_js])

tw2_moksha_ui_popup_js = twc.JSLink(
    filename='public/javascript/ui/moksha.ui.popup.js',
    modname='moksha',
    resources=[tw2.jqplugins.ui.jquery_ui_js])


""" TODO -- why is this included by default in moksha/api/widgets/__init__.py
            It's not very moksha-esque.
"""

class TW1Grid(tw.forms.FormField):
    javascript=[tw.jquery.ui_core.jquery_ui_core_js,
                tw1_moksha_ui_grid_js,
                tw1_moksha_ui_popup_js]
    params= ['rows_per_page', 'page_num', 'total_rows',
            'filters', 'unique_key', 'sort_key', 'sort_order',
            'row_template', 'resource', 'resource_path',
            'loading_throbber', 'uid', 'more_link', 'alphaPager',
            'numericPager', 'morePager']
    hidden = True # hide from the moksha main menu

    rows_per_page = 10
    page_num = 1
    total_rows = 0
    filters = None
    unique_key = None
    sort_key = None
    sort_order = -1
    row_template = None
    resource = None
    resource_path = None
    loading_throbber = None
    more_link = None
    alphaPager = False
    numericPager = False
    morePager = False

    def update_params(self, d):
        super(TW1Grid, self).update_params(d)
        if not getattr(d,"id",None):
            raise ValueError, "Moksha Grid is supposed to have id"

        if not d.filters:
            d.filters = {}

        grid_d = {}
        for p in self.params:
            v = d.get(p)
            if v:
                if isinstance(v, dict):
                    v = json.dumps(v)

                grid_d[p] = v

        d['id'] += "-uuid" + str(uuid.uuid4())

        self.add_call(when_ready(tw.jquery.jQuery("#%s" % d['id']).mokshagrid(grid_d)))


class TW2Grid(tw2.forms.widgets.FormField):
    resources = [tw2.jqplugins.ui.jquery_ui_js,
                 tw2_moksha_ui_grid_js,
                 tw2_moksha_ui_popup_js]
    params= ['rows_per_page', 'page_num', 'total_rows',
            'filters', 'unique_key', 'sort_key', 'sort_order',
            'row_template', 'resource', 'resource_path',
            'loading_throbber', 'uid', 'more_link', 'alphaPager',
            'numericPager']
    hidden = True # hide from the moksha main menu

    rows_per_page = twc.Param(default=10)
    page_num = twc.Param(default=1)
    total_rows = twc.Param(default=0)
    filters = twc.Param(default=None)
    unique_key = twc.Param(default=None)
    sort_key = twc.Param(default=None)
    sort_order = twc.Param(default=-1)
    row_template = twc.Param(default=None)
    resource = twc.Param(default=None)
    resource_path = twc.Param(default=None)
    loading_throbber = twc.Param(default=None)
    more_link = twc.Param(default=None)
    alphaPager = twc.Param(default=False)
    numericPager = twc.Param(default=False)

    def prepare(self):
        super(TW2Grid, self).prepare()

        if not getattr(self, 'id', None):
            raise ValueError, "Moksha Grid is supposed to have id"

        if not self.filters:
            self.filters = {}

        grid_d = {}
        for p in self.params:
            v = getattr(self, p)
            if v:
                if isinstance(v, dict):
                    v = json.dumps(v)

                grid_d[p] = v

        self.id += "-uuid" + str(uuid.uuid4())

        self.add_call(when_ready(tw2.jquery.jQuery("#%s" % self.id).mokshagrid(grid_d)))

if asbool(config.get('moksha.use_tw2', False)):
    Grid = TW2Grid
    moksha_ui_grid_js = tw2_moksha_ui_grid_js
    moksha_ui_popup_js = tw2_moksha_ui_popup_js
else:
    Grid = TW1Grid
    moksha_ui_grid_js = tw1_moksha_ui_grid_js
    moksha_ui_popup_js = tw1_moksha_ui_popup_js

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


import tw.api
import tw.forms
import tw.jquery.ui
import tw.jquery.ui_tabs
import tw2.core as twc
import tw2.forms
import tw2.jqplugins.ui

from pylons import config, request
from repoze.what import predicates
from moksha.lib.helpers import eval_app_config, ConfigWrapper, when_ready
from paste.deploy.converters import asbool

import urllib


tw1_moksha_ui_tabs_js = tw.api.JSLink(
    modname='moksha',
    filename='public/javascript/ui/moksha.ui.tabs.js',
    javascript=[tw.jquery.ui_tabs.jquery_ui_tabs_js,
                tw.jquery.ui.ui_widget_js])

tw2_moksha_ui_tabs_js = twc.JSLink(
    modname='moksha',
    filename='public/javascript/ui/moksha.ui.tabs.js',
    resources=[tw2.jqplugins.ui.jquery_ui_js])


class TW1TabbedContainerTabs(tw.api.Widget):
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer_tabs'


class TW2TabbedContainerTabs(twc.Widget):
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer_tabs'


class TW1TabbedContainerPanes(tw.api.Widget):
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer_panes'


class TW2TabbedContainerPanes(twc.Widget):
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer_panes'


if asbool(config.get('moksha.use_tw2', False)):
    TabbedContainerTabs = TW2TabbedContainerTabs
    TabbedContainerPanes = TW2TabbedContainerPanes
    tabwidget = TabbedContainerTabs(id='tabs')
    panewidget = TabbedContainerPanes(id='panes')
else:
    TabbedContainerTabs = TW1TabbedContainerTabs
    TabbedContainerPanes = TW1TabbedContainerPanes
    tabwidget = TabbedContainerTabs('tabs')
    panewidget = TabbedContainerPanes('panes')


class TW1TabbedContainer(tw.forms.FormField):
    """
    :tabs: An ordered list of application tabs to display
           Application descriptors come from the config wrappers in
           moksha.lib.helpers

           tabs can either be in serialized string format or as a list of
           config wrapper objects.  Using strings means you don't have to
           import the wrappers and predicates but can get unwieldy if there
           is a long list of wrappers

    :config_key: the configuration key used to store the serialized tab config
                 in a configuration file instead of embeding it in the widget

    :template: you must provide a template in order to get styling correct.  The
               default template has minimal functionality.  The documentation
               for jQuery.UI.Tabs can be found at http://ui.jquery.org.
               FIXME: Write a tutorial and provide helper widgets so
               creating a template becomes really easy.
    """
    css=[] # remove the default css
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer'
    config_key = None # if set load config
    tabs = ()
    javascript = [tw1_moksha_ui_tabs_js]
    params = ["tabdefault", "staticLoadOnClick"]
    tabdefault__doc="0-based index of the tab to be selected on page load"
    tabdefault=0
    staticLoadOnClick=False
#    include_dynamic_js_calls = True #????
    def update_params(self, d):
        super(TW1TabbedContainer, self).update_params(d)
        if not getattr(d,"id",None):
            raise ValueError, "JQueryUITabs is supposed to have id"

        o = {
             'tabdefault': d.get('tabdefault', 0),
             'staticLoadOnClick': d.get('staticLoadOnClick', False)
            }
        self.add_call(when_ready(
            tw.jquery.jQuery("#%s" % d.id).mokshatabs(o)))

        tabs = eval_app_config(config.get(self.config_key, "None"))
        if not tabs:
            if isinstance(self.tabs, str):
                tabs = eval_app_config(self.tabs)
            else:
                tabs = self.tabs

        # Filter out any None's in the list which signify apps which are
        # not allowed to run with the current session's authorization level
        tabs = ConfigWrapper.process_wrappers(tabs, d)

        d['tabs'] = tabs
        d['tabwidget'] = tabwidget
        d['panewidget'] = panewidget
        d['root_id'] = d['id']


class TW2TabbedContainer(tw2.forms.widgets.FormField):
    """
    :tabs: An ordered list of application tabs to display
           Application descriptors come from the config wrappers in
           moksha.lib.helpers

           tabs can either be in serialized string format or as a list of
           config wrapper objects.  Using strings means you don't have to
           import the wrappers and predicates but can get unwieldy if there
           is a long list of wrappers

    :config_key: the configuration key used to store the serialized tab config
                 in a configuration file instead of embeding it in the widget

    :template: you must provide a template in order to get styling correct.  The
               default template has minimal functionality.  The documentation
               for jQuery.UI.Tabs can be found at http://ui.jquery.org.
               FIXME: Write a tutorial and provide helper widgets so
               creating a template becomes really easy.
    """
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer'
    resources = [tw2_moksha_ui_tabs_js]

    config_key = twc.Param(default=None)
    tabs = twc.Param(default=())
    params = ["tabdefault", "staticLoadOnClick"]
    tabdefault = twc.Param(
        "0-based index of the tab to be selected on page load",
        default=0)
    staticLoadOnClick = twc.Param(default=False)

    def prepare(self):
        super(TW2TabbedContainer, self).prepare()
        if not getattr(self, "id", None):
            raise ValueError, "JQueryUITabs is supposed to have id"

        o = {
            'tabdefault': self.tabdefault,
            'staticLoadOnClick': self.staticLoadOnClick
        }
        self.add_call(when_ready(
            tw2.jquery.jQuery("#%s" % self.id).mokshatabs(o)))

        tabs = eval_app_config(config.get(self.config_key, "None"))
        if not tabs:
            if isinstance(self.tabs, str):
                tabs = eval_app_config(self.tabs)
            else:
                tabs = self.tabs

        # Filter out any None's in the list which signify apps which are
        # not allowed to run with the current session's authorization level
        tabs = ConfigWrapper.process_wrappers(tabs, self)

        self.tabs = tabs
        self.tabwidget = tabwidget
        self.panewidget = panewidget
        self.root_id = id


if asbool(config.get('moksha.use_tw2', False)):
    TabbedContainer = TW2TabbedContainer
    moksha_ui_tabs_js = tw2_moksha_ui_tabs_js
else:
    TabbedContainer = TW1TabbedContainer
    moksha_ui_tabs_js = tw1_moksha_ui_tabs_js

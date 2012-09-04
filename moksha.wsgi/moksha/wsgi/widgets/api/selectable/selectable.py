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


import tw2.core as twc
import tw2.jquery
import tw2.jqplugins.ui

from uuid import uuid4


moksha_ui_selectable_js = twc.JSLink(
    modname='moksha',
    filename='public/javascript/ui/moksha.ui.selectable.js',
    resources=[tw2.jqplugins.ui.jquery_ui_js])


class Selectable(twc.Widget):
    template = 'mako:moksha.wsgi.widgets.api.selectable.templates.selectable'
    resources = [moksha_ui_selectable_js]

    def prepare(self):
        super(Selectable, self).prepare()
        content_id = d.id + '-uuid' + str(uuid4())
        self.content_id = content_id

        self.add_call(
            tw2.jquery.jQuery("#%s" % self.content_id).moksha_selectable())

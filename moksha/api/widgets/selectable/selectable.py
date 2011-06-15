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


from tg import config
from paste.deploy.converters import asbool

import tw.api
from tw.jquery.ui_core import jquery_ui_core_js
from tw.jquery import jQuery, jquery_js
from uuid import uuid4

tw1_moksha_ui_selectable_js = tw.api.JSLink(
    modname='moksha',
    filename='public/javascript/ui/moksha.ui.selectable.js',
    javascript=[jquery_ui_core_js])

class TW1Selectable(tw.api.Widget):
    template = 'mako:moksha.api.widgets.selectable.templates.selectable'
    javascript = [tw1_moksha_ui_selectable_js]

    def update_params(self, d):
        super(TW1Selectable, self).update_params(d)
        content_id = d.id + '-uuid' + str(uuid4())
        d['content_id'] = content_id

        self.add_call(jQuery("#%s" % d.content_id).moksha_selectable())

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    Selectable = TW1Selectable
    moksha_ui_selectable_js = tw1_moksha_ui_selectable_js


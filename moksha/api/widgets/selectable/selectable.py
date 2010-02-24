# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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

from tw.api import JSLink, Widget
from tw.jquery.ui_core import jquery_ui_core_js
from tw.jquery import jQuery, jquery_js
from uuid import uuid4


moksha_ui_selectable_js = JSLink(modname='moksha', filename='public/javascript/ui/moksha.ui.selectable.js',
                              javascript=[jquery_ui_core_js])

class Selectable(Widget):
    template = 'mako:moksha.api.widgets.selectable.templates.selectable'
    javascript = [moksha_ui_selectable_js]

    def update_params(self, d):
        super(Selectable, self).update_params(d)
        content_id = d.id + '-uuid' + str(uuid4())
        d['content_id'] = content_id

        self.add_call(jQuery("#%s" % d.content_id).moksha_selectable())


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

import moksha
import moksha.utils

from tg import expose, redirect
from moksha.lib.base import Controller

class MokshaMenuController(Controller):
    name = 'Moksha Menus'

    @expose()
    def _default(self, menuId, *args, **kw):
        """ For the selected `menuId`, return the menu HTML.

        The `menuId` is the name of the portion of the menu that was clicked
        on.  For example, if the menu name was 'default_menu', and the first
        section was called 'Help', then the menuId would be 'default_menu_help'.
        This controller will then call the help() method on the
        MokshaModel.
        """
        split = menuId.lower().split('_')
        menu_id = '_'.join(split[:-1])
        menu_item = split[-1]
        try:
            menu = getattr(moksha.utils.menus[menu_id], menu_item)(**kw)
        except KeyError, e:
            # For the widget demo, just use the default menu
            if menu_id == 'test_widget':
                menu_id = 'default_menu'
                menu = getattr(moksha.utils.menus[menu_id], menu_item)(**kw)
            else:
                redirect('/404')
        return """
            <div id="%(menuId)s" class="menu">
                %(menu)s
            </div>
        """ % {'menuId': menuId, 'menu': menu}


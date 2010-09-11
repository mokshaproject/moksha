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

import moksha

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
            menu = getattr(moksha.menus[menu_id], menu_item)(**kw)
        except KeyError, e:
            # For the widget demo, just use the default menu
            if menu_id == 'test_widget':
                menu_id = 'default_menu'
                menu = getattr(moksha.menus[menu_id], menu_item)(**kw)
            else:
                redirect('/404')
        return """
            <div id="%(menuId)s" class="menu">
                %(menu)s
            </div>
        """ % {'menuId': menuId, 'menu': menu}


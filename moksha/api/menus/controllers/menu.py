# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import moksha

from tg import expose
from moksha.lib.base import Controller

class MokshaMenuController(Controller):
    name = 'Moksha Menus'

    @expose()
    def default(self, menuId, *args, **kw):
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
        menu = getattr(moksha.menus[menu_id], menu_item)(**kw)
        return """
            <div id="%(menuId)s" class="menu">
                %(menu)s
            </div>
        """ % {'menuId': menuId, 'menu': menu}

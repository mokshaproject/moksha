# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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
#
# Authors: Luke Macken <lmacken@redhat.com>

from tg.controllers import WSGIAppController
from pylons import cache
from moksha.widgetbrowser import WidgetBrowser

from moksha.widgets.feedtree import moksha_feedreader
from moksha.controllers.apps import AppController

app_controller = WSGIAppController(AppController())

@WidgetBrowser.register_controller(moksha_feedreader, '/apps/feeds/init_tree')
def init_tree(self, key, fresh=False, **kw):
    return app_controller

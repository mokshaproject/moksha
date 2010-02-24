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

from tw.api import Widget
from pylons import tmpl_context

class ContextAwareWidget(Widget):
    '''Inherit from this widget class if you want your widget
       to automatically get the pylons.tmpl_context in its dictionary
    '''

    def update_params(self, d):
        super(ContextAwareWidget, self).update_params(d)

        d['tmpl_context'] = tmpl_context
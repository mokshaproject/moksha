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

class Placeholder(Widget):
    engine_name = 'mako'
    hidden = True
    template = """
<p class='placeholder'>
    Moksha application <strong>${appname}</strong> is not registered yet.  This is a placeholder
    for testing purposes.  When the app is registered it will appear in the
    layout once the server is restarted.
</p>
"""

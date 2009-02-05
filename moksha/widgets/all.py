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

"""
A module that imports all known widgets.

This is currently used by the `archive_tw_resources` setuptools command,
which archives all of the resources used by all ToscaWidgets.
"""

import pkg_resources
from inspect import isclass

__all__ = []

for entry_point in ('moksha.widget', 'moksha.menu', 'moksha.global'):
    for widget_entry in pkg_resources.iter_entry_points(entry_point):
        widget_class = widget_entry.load()
        if isclass(widget_class):
            widget = widget_class(widget_entry.name)
        else:
            widget = widget_class
        __all__.append(widget)

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

"""
A module that imports all known widgets.

This is currently used by the `archive_tw_resources` setuptools command,
which archives all of the resources used by all ToscaWidgets.
"""

import pkg_resources

from tw.api import Widget
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

# Other stuff that isn't exposed
from moksha.widgets.container import MokshaContainer
__all__.append(MokshaContainer)
from moksha.widgets.notify import MokshaNotificationWidget
__all__.append(MokshaNotificationWidget)

from moksha.widgetbrowser import widgets
for obj in dir(widgets):
    if isinstance(getattr(widgets, obj), Widget):
        __all__.append(obj)

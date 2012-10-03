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

# The root controller class
root = None

# The central feed cache, used by the Feed widget.
feed_cache = None

# A dict-like persistent backing store
feed_storage = None

# All loaded moksha applications
_apps = None

# All loaded ToscaWidgets
_widgets = None

# All WSGI applications
wsgiapps = None

# All loaded moksha menus
menus = None

def get_widget(name):
    """ Get a widget instance by name """
    if _widgets:
        return _widgets[name]['widget']

def get_widgets():
    """ Return a dictionary of all widgets """
    from pkg_resources import iter_entry_points
    return _widgets or [widget.load() for widget in iter_entry_points('moksha.widget')]

def get_app(name):
    """ Get an app controller by name """
    return _apps[name]['controller']

def shutdown():
    """ Called when Moksha shuts down """
    try:
        if feed_storage:
            feed_storage.close()
    except AttributeError:
        pass

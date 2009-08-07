__import__('pkg_resources').declare_namespace(__name__)

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

from paste.registry import StackedObjectProxy

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

# Per-request stomp callbacks registered by rendered widget
stomp = StackedObjectProxy()

def get_widget(name):
    """ Get a widget instance by name """
    return _widgets[name]['widget']

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

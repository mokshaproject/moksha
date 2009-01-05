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
# Authors: John (J5) Palmieri <johnp@redhat.com>

class IConnector(object):
    def register(self):
        pass
    
    def request_data(self, **params):
        pass
    
    def introspect(self):
        pass

class ICall(object):
    def call(self, **params):
        pass

class ITable(object):
    def query(self, **params):
        pass

class IFeed(object):
    def request_feed(self, **params):
        pass

class INotify(object):
    def register_listener(self, listener_cb):
        pass
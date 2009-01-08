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

from tw.api import Widget
from moksha.stomp import stomp_widget

class LiveWidget(Widget):
    """
    This class turns a widget into a live streaming widget.  It injects the
    StompWidget, and configures it with any existing callbacks in your widget.
    """
    def __new__(cls, id=None, parent=None, children=[], **kw):
        obj = Widget.__new__(cls, id, parent, children, **kw)
        obj.children.append(stomp_widget)
        stomp_args = ''
        for callback in stomp_widget.params:
            if callback in obj.params:
                stomp_args += "%s=%s," % (callback, callback)
        obj.template += "${c.stomp(%s)}" % (stomp_args[:-1])
        return obj


class NewParentLiveWidget(Widget):
    """
    This class turns a widget into a live streaming widget.  It injects the
    StompWidget, and configures it with any existing callbacks in your widget.

              Does this matter?  Can't we do something like this at 
              instantiation?

                widget.template += "stomp(${stomp_args})"

             then in update_params()

                callbacks = []
                # get subclass's callbacks from D
                d['stomp_args'] = join callbacks...
    """
    params = ['stomp_args']
    def __new__(cls, id=None, parent=None, children=[], **kw):
        obj = Widget.__new__(cls, id, parent, children, **kw)
        obj.children.append(stomp_widget)
        stomp_args = ''
        for callback in stomp_widget.params:
            if callback in obj.params:
                stomp_args += "%s=%s," % (callback, callback)
        obj.template += "${c.stomp(stomp_args)}"
        #obj.template += "${c.stomp(%s)}" % (stomp_args[:-1])
        return obj

    def update_params(self, d):
        """
        Register all of this widgets stomp callbacks.
        """
        super(LiveWidget, self).update_params(d)
        stomp_args = ''
        print "callbacks =", stomp_widget.callbacks
        for callback in stomp_widget.callbacks:
            if callback in self.params:
                stomp_args += "%s=%s," % (callback, callback)
        d['stomp_args'] = stomp_args[:-1]
        print "stomp_args = %r" % d['stomp_args']
        print "self.params = %r" % self.params
        #print "self.template = %r" % self.template

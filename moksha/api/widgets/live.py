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

from tw.api import Widget
from moksha.exc import MokshaException
from moksha.api.widgets.stomp import stomp_widget, stomp_subscribe

class LiveWidget(Widget):
    """ A live streaming widget.

    This widget handles automatically subscribing your widget to any given
    topics, and registers all of the stomp callbacks.
    """
    engine_name = 'mako'

    def update_params(self, d):
        """ Register this widgets stomp callbacks """
        super(LiveWidget, self).update_params(d)
        topics = d.get('topic', getattr(self, 'topic', None))
        if not topics:
            raise MokshaException('You must specify a `topic` to subscribe to')
        topics = isinstance(topics, list) and topics or [topics]
        for callback in stomp_widget.callbacks:
            if callback == 'onmessageframe':
                for topic in topics:
                    cb = getattr(self, 'onmessage').replace('${id}', self.id)
                    moksha.stomp[callback][topic].append(cb)
            elif callback == 'onconnectedframe':
                moksha.stomp['onconnectedframe'].append(stomp_subscribe(topics))
            elif callback in self.params:
                moksha.stomp[callback].append(getattr(self, callback))

import tw2.core as twc
from tw2.jqplugins.gritter import gritter_resources, gritter_callback

from moksha.wsgi.widgets.moksha_js import moksha_js
from moksha.common.lib.helpers import defaultdict
import moksha.wsgi.lib.utils


class AbstractMokshaSocket(twc.Widget):
    """ Abstract socket widget from which the AMQPSocket, STOMPSocket and
    WebSocketSocket inherit.

    NOTE - this only exists for tw2.  I'm not bothering with refactoring tw1
    code now.
    """

    __shorthand__ = twc.Variable(default=None)

    resources = [moksha_js]
    topics = twc.Variable()

    hidden = twc.Variable(default=True)

    notify = twc.Param(default=twc.Required)
    reconnect_interval = twc.Param(default=twc.Required)

    callbacks = [
        "onopen",
        "onclose",
        "onerror",
        "onconnectedframe",
        "onmessageframe",
        "onerrorframe",
    ]

    onopen = twc.Param(default='function (e) {moksha.debug(e)}')
    onclose = twc.Param(default='function (e) {moksha.debug(e)}')
    onerror = twc.Param(default='function (e) {moksha.debug(e)}')
    onerrorframe = twc.Param(default='function (e) {moksha.debug(e)}')
    onconnectedframe = twc.Param(default='function (e) {moksha.debug(e)}')

    # Used internally
    before_open = twc.Variable(default='function () {}')

    notifications = {
        'before_open': 'Attempting to connect Moksha Live Socket',
        'onconnectedframe': 'Moksha Live socket connected',  # AMQP, STOMP
        'onopen': 'Moksha Live socket connected',            # WebSocket
        'onclose': 'Moksha Live socket closed',
        'onerrorframe': 'Error with Moksha Live socket',
        'onerror': 'Error with Moksha Live socket',
    }

    def prepare(self):
        super(AbstractMokshaSocket, self).prepare()

        if not self.__shorthand__:
            raise ValueError("SocketWidget must declare __shorthand__")

        self.topics = []
        self.onmessageframe = defaultdict(str)

        if self.notify:
            self.resources += gritter_resources
            self.before_open = "$(%s);" % unicode(gritter_callback(
                title=self.__shorthand__,
                text=self.notifications['before_open'],
            ))

        for callback in self.callbacks:
            cbs = ''

            if self.notify and callback in self.notifications:
                cbs += "$(%s);" % unicode(gritter_callback(
                    title=self.__shorthand__,
                    text=self.notifications[callback]
                ))

            if self.reconnect_interval and callback is 'onclose':
                cbs += "setTimeout(setup_moksha_socket, %i)" % \
                        int(self.reconnect_interval)

            if len(moksha.wsgi.lib.utils.livewidgets[callback]):
                if callback == 'onmessageframe':
                    for topic in moksha.wsgi.lib.utils.livewidgets[callback]:
                        self.topics.append(topic)
                        for cb in moksha.wsgi.lib.utils.livewidgets[callback][topic]:
                            self.onmessageframe[topic] += '%s;' % unicode(cb)
                else:
                    for cb in moksha.wsgi.lib.utils.livewidgets[callback]:
                        if isinstance(cb, (twc.js_callback, twc.js_function)):
                            cbs += '$(%s);' % unicode(cb)
                        else:
                            cbs += unicode(cb)
            if cbs:
                setattr(self, callback, cbs)


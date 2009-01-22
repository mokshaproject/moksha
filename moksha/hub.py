import pkg_resources
import logging
log = logging.getLogger(__name__)

from collections import defaultdict
from threading import Thread

from twisted.internet import reactor
from twisted.internet.threads import deferToThread
deferred = deferToThread.__get__

from moksha.api.hub import Consumer
from moksha.lib.utils import trace


class MokshaConsumer(Consumer):
    queue = 'testing'
    def consume(self, message):
        print "MokshaConsumer.consume(%s)" % message.body


# @@ Caveats
# At the moment, the queue name must be equal to the routing key.
# This may cause limitations in the future, but for now it necessary
# because we need to take the `routing_key` on an AMQP message, and deliver
# it to a consumer who is watching a specific `queue`.  Since AMQP messages
# do not contain the queue name, they need to be the same.

from moksha.amqp import AMQPLibHub

class MokshaHub(AMQPLibHub):
    """
    The Moksha Hub is responsible for initializing all of the Hooks,
    AMQP queues, exchanges, etc.
    """
    conn = None
    queues = None # {queue_name: [callback,]}
    consumers = None # {queue_name: [<Consumer instance>,]}
    data_streams = None

    def __init__(self, broker='127.0.0.1:5672', username='guest',
                 password='guest', ssl=False, main=False):
        super(MokshaHub, self).__init__(broker, username=username, 
                                        password=password, ssl=ssl)
        self.queues = defaultdict(list)
        if main:
            self.__init_main_hub()

    def __init_main_hub(self):
        """ Initialize various items for the central Moksha hub """
        log.debug('Initializing the main MokshaHub')
        self.__init_consumers()
        self.__init_data_streams()

    def __init_consumers(self):
        """ Initialize all Moksha Consumer objects """
        self.consumers = defaultdict(list)
        for consumer in pkg_resources.iter_entry_points('moksha.consumer'):
            c_class = consumer.load()
            log.info('Loading %s consumer' % c_class.__name__)
            c = c_class()
            self.consumers[c.queue].append(c)
            log.debug("%s consumer is watching the %r queue" % (
                      c_class.__name__, c.queue))
            self.watch_queue(c.queue, callback=lambda msg: c.consume(msg))

    def __init_data_streams(self):
        """ Initialize all data streams """
        self.data_streams = []
        for stream in pkg_resources.iter_entry_points('moksha.stream'):
            stream_class = stream.load()
            log.info('Loading %s data stream' % stream_class.__name__)
            stream_obj = stream_class()
            self.data_streams.append(stream_obj)

    @trace
    def watch_queue(self, queue, callback):
        """
        This method will cause the specified `callback` to be executed with
        each message that goes through a given queue.
        """
        if len(self.queues[queue]) == 0:
            self.consume(queue, callback=self.consume_message, no_ack=True)
        self.queues[queue].append(callback)

    @trace
    def consume_message(self, message):
        """ The main Moksha message consumer.

        This method receives every message for every queue that is being 
        "watched", via the :meth:MokshaHub.watch_queue, or by a :class:`Hook`.
        It will then call
        """
        for callback in self.queues[message.delivery_info['routing_key']]:
            log.debug("calling %s" % callback)
            Thread(target=callback, args=[message]).start()

    @deferred
    def start(self):
        """ The MokshaHub's main loop """
        log.debug('MokshaHub.start()')
        while self.channel.callbacks:
            try:
                self.channel.wait()
            except Exception, e:
                log.warning('Exception thrown while waiting on AMQP '
                            'channel: %s' % str(e))
                break
        log.debug('No more channel callbacks; MokshaHub.start complete!')

    def stop(self):
        log.debug("Stopping the MokshaHub")
        if self.data_streams:
            for stream in self.data_streams:
                log.debug("Stopping data stream %s" % stream)
                stream.stop()
        try:
            self.close()
        except Exception, e:
            log.warning('Exception when closing AMQPHub: %s' % str(e))


def main():
    hub = MokshaHub(main=True)
    hub.create_queue("testing")
    hub.queue_bind("testing", "amq.topic")
    hub.send_message('foo', exchange='amq.topic', routing_key='testing')

    def callback(msg):
        for key, val in msg.properties.items():
            print '%s: %s' % (key, str(val))
        for key, val in msg.delivery_info.items():
            print '> %s: %s' % (key, str(val))
        print ''
        print msg.body
        print '-------'

    hub.watch_queue('testing', callback=callback)
    hub.send_message('bar', exchange='amq.topic', routing_key='testing')
    hub.start(hub)

    # @@ Fix this crap and make this exit cleanly...
    import os
    import sys
    import signal
    def handle_signal(signum, stackframe):
        print "handle_signal!"
        from twisted.internet import reactor
        if signum in [signal.SIGHUP, signal.SIGINT]:
            reactor.stop()
            hub.stop()
            sys.exit(0)
    signal.signal(signal.SIGHUP, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    print "Running the reactor!"
    reactor.run(installSignalHandlers=False)
    print "Reactor stopped!"

def setup_logger(verbose):
    global log
    sh = logging.StreamHandler()
    level = verbose and logging.DEBUG or logging.INFO
    log.setLevel(level)
    sh.setLevel(level)
    format = logging.Formatter("%(message)s")
    sh.setFormatter(format)
    log.addHandler(sh)

if __name__ == '__main__':
    import sys
    setup_logger('-v' in sys.argv or '--verbose' in sys.argv)
    main()

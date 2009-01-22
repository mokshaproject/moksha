import pkg_resources
import logging
log = logging.getLogger(__name__)

from collections import defaultdict
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
deferred = deferToThread.__get__

from moksha.api.hub import Consumer

class MokshaConsumer(Consumer):
    queue = 'testing'
    def consume(self, message):
        print "MyHook.consume(%s)" % message.body


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
    #topics = None
    queues = None # {queue_name: [callback,]}
    consumers = None # {queue_name: [<Consumer instance>,]}
    data_streams = None

    def __init__(self, broker='127.0.0.1:5672', username='guest',
                 password='guest', ssl=False, main=False):
        super(MokshaHub, self).__init__(broker, username=username, 
                                        password=password, ssl=ssl)
        self.queues = {}
        if main:
            self.__init_main_hub()

    def __init_main_hub(self):
        """ Initialize various items for the central Moksha hub """
        log.debug('Initializing the main MokshaHub')
        self.__init_consumers()
        self.__init_data_streams()
        #self.__init_topics()
        #self.__init_queues()

    #def __init_topics(self):
    #    """ Initialize all "topics" from queues that consumers are watching """
    #    self.topics = set()
    #    for consumer in self.consumers:
    #        self.topics.add(consumer.queue)

    def __init_consumers(self):
        """ Initialize all Moksha Consumer objects """
        self.consumers = defaultdict(list)
        for consumer in pkg_resources.iter_entry_points('moksha.consumer'):
            c_class = consumer.load()
            log.info('Initializing %s consumer' % c_class.__name__)
            c = c_class()
            self.consumers[c.queue].append(c)
            log.debug("%s consumer is watching the %r queue" % (
                      c_class.__name__, c.queue))
            self.watch_queue(c.queue, callback=lambda msg: c.consume(msg))

    #def __init_queues(self):
    #    """ Declare and bind queues for each topic in self.topics """
    #    self.queues = {}
    #    for topic in self.topics:
    #        if not topic in self.queues:
    #            self.create_queue(topic)
    #            self.queue_bind(topic, 'amq.topic')

    def __init_data_streams(self):
        """ Initialize all data streams """
        log.info('Initializing data streams')
        self.data_streams = []
        # @@ dynamically suck these in from an entry point
        #from moksha.streams.feed import FeedStream
        from moksha.streams.demo import MokshaDemoDataStream
        streams = [MokshaDemoDataStream]
        for stream in streams:
            self.data_streams.append(stream())

    def watch_queue(self, queue, callback):
        """
        This method will cause the specified `callback` to be executed with
        each message that goes through a given queue.
        """
        log.debug("watch_queue(%s)" % locals())
        if not queue in self.queues:
            self.create_queue(queue)
            self.queue_bind(queue, 'amq.topic')
        if len(self.queues[queue]) == 0:
            self.consume(queue, callback=self.consume_message, no_ack=True)
        self.queues[queue].append(callback)

    def consume_message(self, message):
        """ The main Moksha message consumer.

        This method receives every message for every queue that is being 
        "watched", via the :meth:MokshaHub.watch_queue, or by a :class:`Hook`.
        It will then call
        """
        log.debug("consume_message(%s)" % message)
        for callback in self.queues.get(message.delivery_info['routing_key'], []):
            log.debug("calling %s" % callback)
            callback(message)

    @deferred
    def start(self):
        """ The MokshaHub's main loop """
        while self.channel.callbacks:
            self.channel.wait()
        print "self.channel =", self.channel
        print self.channel.callbacks

    def stop(self):
        log.debug("Stopping the MokshaHub")
        if self.data_streams:
            for source in self.data_streams:
                log.debug("Stopping data stream %s" % source)
                source.timer.stop()
        if self.channel:
            self.channel.close()
        if self.conn:
            self.conn.close()
    __del__ = stop


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
    hub.send_message('bar', routing_key='testing')
    hub.start(hub)

    # @@ Make this exit cleanly...
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

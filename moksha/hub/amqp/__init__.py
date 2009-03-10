"""
Here is where we configure which AMQP hub implementation we are going to use.
"""
import logging
log = logging.getLogger(__name__)

try:
    from qpid010 import QpidAMQPHub
    AMQPHub = QpidAMQPHub
except ImportError:
    log.debug("Unable to import qpid module")
    class FakeHub(object):
        pass
    AMQPHub = FakeHub

#from pyamqplib import AMQPLibHub
#AMQPHub = AMQPLibHub

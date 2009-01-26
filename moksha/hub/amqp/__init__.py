"""
Here is where we configure which AMQP hub implementation we are going to use.
"""

from qpid010 import QpidAMQPHub
AMQPHub = QpidAMQPHub

#from pyamqplib import AMQPLibHub
#AMQPHub = AMQPLibHub

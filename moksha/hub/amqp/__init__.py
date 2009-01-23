"""
Here is where we configure which AMQP hub implementation we are going to use.
"""
# from qpid import QpidAMQP08Hub
from pyamqplib import AMQPLibHub
AMQPHub = AMQPLibHub

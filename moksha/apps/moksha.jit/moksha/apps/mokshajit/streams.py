#import logging
#log = logging.getLogger('moksha.hub')

from datetime import timedelta, datetime
from moksha.api.hub.producer import PollingProducer

class MokshajitStream(PollingProducer):
    frequency = timedelta(seconds=3)
    topic = 'moksha.jit'
    i = 0

    def poll(self):
        """ This method is called by the MokshaHub reactor every `frequency` """
        self.i += 1
        self.send_message(self.topic, {'message': self.i})

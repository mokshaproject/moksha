from datetime import timedelta
from moksha.api.hub.producer import PollingProducer

class HelloWorldProducer(PollingProducer):
    frequency = timedelta(seconds=3)

    def poll(self):
        self.send_message('helloworld', {'msg': 'Hello World!'})

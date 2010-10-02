from moksha.api.hub.producer import PollingProducer
from datetime import timedelta

class HelloWorldProducer(PollingProducer):
    frequency = timedelta(seconds=3)

    def poll(self):
        self.send_message('helloworld', {'msg': 'Hello World!'})

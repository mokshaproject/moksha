from moksha.api.hub.consumer import Consumer
from demo.model import HelloWorldModel

class HelloWorldConsumer(Consumer):
    topic = 'helloworld'
    app = 'helloworld'

    def consume(self, message):
        self.log.info('Received message: ' + message['body']['msg'])

        entry = HelloWorldModel()
        entry.message = message['body']['msg']
        self.DBSession.add(entry)
        self.DBSession.commit()

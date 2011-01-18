from moksha.api.hub.consumer import Consumer
from demo.model import HelloWorldModel

class HelloWorldConsumer(Consumer):
    topic = 'helloworld'
    app = 'helloworld'
    i = 0

    def consume(self, message):
        self.log.info('Received message: ' + message['body']['msg'])

        entry = HelloWorldModel()
        entry.message = message['body']['msg']
        self.DBSession.add(entry)

        self.i += 1
        if self.i % 100 == 0:
            self.DBSession.commit()


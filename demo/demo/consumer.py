from moksha.api.hub.consumer import Consumer

class HelloWorldConsumer(Consumer):
    topic = 'helloworld'

    def consume(self, message):
        self.log.info('Received message: ' + message['body']['msg'])

from moksha.apps.knowledge.model import Entity
from moksha.api.hub import Consumer

class TopicsConsumer(Consumer):
    topic = '#' # subscribe to all topics
    app = 'moksha.apps.knowledge' # automagically setup SA engine & DBSession

    _topic_cache = {}

    def consume(self, message):
        #self.log.info("%r entities " % self.DBSession.query(Entity).count())
        topics = []
        commit = False
        for header in message.headers:
            topics.append(header.routing_key)
        for topic in topics:
            if topic not in self._topic_cache:
                if not self.DBSession.query(Entity).filter_by(name=topic).first():
                    self.log.debug('Found new topic: ' + topic)
                    self._topic_cache[topic] = None
                    entity = Entity(topic)
                    self.DBSession.add(entity)
                    commit = True
        if commit:
            self.DBSession.commit()

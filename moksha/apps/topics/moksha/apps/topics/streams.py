import pkg_resources
import logging
log = logging.getLogger('moksha.hub')

from datetime import timedelta
from kitchen.text.converters import to_unicode

from moksha.api.streams import PollingDataStream
from moksha.apps.knowledge.model import Entity
from moksha.lib.helpers import listify, defaultdict

class TopicsStream(PollingDataStream):
    frequency = timedelta(hours=1)
    topic = 'org.moksha.topics.new'
    now = True
    app = 'moksha.apps.knowledge' # automagically setup SA engine & DBSession

    def poll(self):
        reload(pkg_resources)
        topics = set()
        for entry in (u'moksha.widget', u'moksha.stream', u'moksha.consumer'):
            for entry_topic, entries in self.crawl_moksha_topics(entry).items():
                if entry_topic:
                    if not self.DBSession.query(Entity).filter_by(name=entry_topic).first():
                        msg = 'New topic found: %s' % entry_topic
                        log.info(msg)
                        entity = Entity(entry_topic)
                        entity[entry] = entries
                        self.DBSession.add(entity)
                        self.send_message(self.topic, msg)
        self.DBSession.commit()

    def crawl_moksha_topics(self, entry_point='moksha.widget'):
        """ Iterate over all moksha widgets looking for topics """
        topics = defaultdict(list)
        for entry in pkg_resources.iter_entry_points(entry_point):
            entry_class = entry.load()
            for topic in listify(getattr(entry_class, 'topic', [])):
                topics[to_unicode(topic)].append(entry_class)
            for topic in listify(getattr(entry_class, 'topics', [])):
                topics[to_unicode(topic)].append(entry_class)
        return topics

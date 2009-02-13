# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import moksha
import logging
import feedparser, time, sys
import md5, os

try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO

from twisted.web import client
from twisted.web.client import HTTPPageGetter, HTTPClientFactory
from twisted.internet import reactor, protocol, defer, ssl
from twisted.web import error
from datetime import timedelta, datetime
from feedcache import Cache
from shove import Shove
from tg import config

from moksha.api.streams import PollingDataStream
from moksha.lib.helpers import trace

log = logging.getLogger('moksha.hub')

feed_storage = Shove(config['feed_cache'], compress=True)
feed_cache = Cache(feed_storage)

class ConditionalHTTPPageGetter(HTTPPageGetter):

    def handleStatus_200(self):
        """ If we're good, try recording the last-modified header """
        if self.headers.has_key('last-modified'):
            self.factory.lastModified(self.headers['last-modified'])

    def handleStatus_304(self):
        """ Close connection """
        self.factory.notModified()
        self.transport.loseConnection()


class ConditionalHTTPClientFactory(HTTPClientFactory):

    protocol = ConditionalHTTPPageGetter

    def __init__(self, url, method='GET', postdata=None, headers=None,
                 agent="Moksha Feed Streamer", timeout=0, cookies=None,
                 followRedirect=1):

        self.url = url

        if url in feed_storage:
            lastModified = time.ctime(feed_storage[url][0])
            if headers is not None:
                headers['last-modified'] = lastModified
            else:
                headers = {'last-modified': lastModified}

        HTTPClientFactory.__init__(self, url, method=method, postdata=postdata,
                headers=headers, agent=agent, timeout=timeout, cookies=cookies,
                followRedirect=followRedirect)

        self.waiting = True
        self.deferred = defer.Deferred()

    def lastModified(self, modtime):
        t = time.mktime(time.strptime(modtime[0], '%a, %d %b %Y %H:%M:%S %Z'))
        parsed_feed = {}

        if self.url in feed_storage:
            current_feed = feed_storage[self.url][1]
            if current_feed and not current_feed.get('bozo_exception'):
                parsed_feed = current_feed

        try:
            feed_storage[self.url] = (t, parsed_feed)
        except:
            log.error("Unable to store parsed_feed: %r" % parsed_feed)
            raise

    def notModified():
        if self.waiting:
            self.waiting = False


def conditional_get_page(url, contextFactory=None, *args, **kwargs):
    scheme, host, port, path = client._parse(url)
    factory = ConditionalHTTPClientFactory(url, *args, **kwargs)
    if scheme == 'https':
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory.deferred


class FeederProtocol(object):

    max_age = int(config.get('feed.max_age', 300))
    timeout = int(config.get('feed.timeout', 30))

    def __init__(self):
        self.parsed = 1
        self.with_errors = 0
        self.error_list = []

    def is_cached(self, site):
        already_got = feed_storage.get(site[0])
        if already_got:
            elapsed_time = time.time() - already_got[0]
            if elapsed_time < self.max_age:
                return True
            else:
                return False
        else:
            return False

    def on_error(self, traceback, extra_args):
        log.error(extra_args)
        log.exception(traceback)
        self.with_errors += 1
        self.error_list.append(extra_args)

    def get_feed_from_cache(self, data, key=None):
        """ Return feed data from the cache based on a given ``key`` """
        log.debug('Getting cached feed for %s' % key)
        return defer.succeed(feed_storage.get(key, key)[1])

    def parse_feed(self, feed, url):
        if not feed:
            log.warning('parse_feed got %r for %s' % (feed, url))
            return {}
        if not isinstance(feed, basestring):
            feed = str(feed)
        feed = feedparser.parse(StringIO(feed))
        assert feed
        if feed.get('bozo_exception'):
            bozo_exc = str(feed['bozo_exception'])
            log.warning("Feed %s getting bozo_exception %r" % (feed, bozo_exc))
            feed['bozo_exception'] = bozo_exc
        return feed

    def store_feed(self, feed, addr):
        feed_storage[addr] = (time.time(), feed)
        return feed

    def process_feed(self, parsed_feed, addr):
        if not parsed_feed:
            log.error("Cannot process %r feed for %s" % (parsed_feed, addr))
            return
        chan = parsed_feed.get('channel', None)
        if chan:
            log.debug(chan.get('title', ''))
        #    print chan.get('link', '')
        #    #print chan.get('tagline', '')
        #    print chan.get('description','')
        #print "-"*20
        #items = parsed_feed.get('items', None)
        #if items:
        #    for item in items:
        #        print '\tTitle: ', item.get('title','')
        #        print '\tDate: ', item.get('date', '')
        #        print '\tLink: ', item.get('link', '')
        #        print '\tDescription: ', item.get('description', '')
        #        print '\tSummary: ', item.get('summary','')
        #        print "-"*20
        #print "got",addr
        #print "="*40
        return parsed_feed

        ## @@ post processing
        for url in feed_storage:
            olddata = feed_storage[url][1].copy()
            newdata = feed_cache.fetch(url) #, force_update=True)
            # If there are no new entries, move on...
            if newdata['entries'][0]['title'] == olddata['entries'][0]['title']:
                log.debug('No feed changes for %s' % url)
                del(olddata)
                continue
            oldtitles = [entry['title'] for entry in olddata['entries']]
            for entry in newdata['entries'][::-1]:
                # If we haven't seen this entry yet...
                if entry['title'] not in oldtitles:
                    # Send a message to the feed's topic
                    print "New entry:", entry['title']
                    self.send_message('feed.%s' % entry.channel.link,
                            {'title': entry['title'], 'link': entry['link']})
                else:
                    print "Dupe entry", entry['title']


    def get_page(self, data, args):
        return conditional_get_page(args, timeout=self.timeout)

    def print_status(self, data=None):
        pass

    def start(self, data=None):
        d = defer.succeed(True)
        for feed in data:
            if self.is_cached(feed):
                d.addCallback(self.get_feed_from_cache, feed[0])
                d.addErrback(self.on_error, (feed[0], 'fetching from cache'))
            else:
                d.addCallback(self.get_page, feed[0])
                d.addErrback(self.on_error, (feed[0], 'fetching'))
                d.addCallback(self.parse_feed, feed[0])
                d.addErrback(self.on_error, (feed[0], 'parsing'))
                d.addCallback(self.store_feed, feed[0])
                d.addErrback(self.on_error, (feed[0], 'storing'))
            d.addCallback(self.process_feed, feed[0])
            d.addErrback(self.on_error, (feed[0], 'processing'))
        return d


class FeederFactory(protocol.ClientFactory):

    protocol = FeederProtocol()

    def __init__(self, deferred_groups=60):
        """Initialize the Feeder Factory.

        :param deferred_groups: The number of simultaneous connections
        """
        self.protocol.factory = self
        self.deferred_groups = deferred_groups

    def start(self, addresses):
        """Divide into groups all the feeds to download.

        :param addresses: A list of feed urls
        """
        log.info("Starting the FeederFactory...")
        if len(addresses) > self.deferred_groups:
            url_groups = [[] for x in xrange(self.deferred_groups)]
            for i, addr in enumerate(addresses):
                url_groups[i % self.deferred_groups].append(addr)
        else:
            url_groups = [[addr] for addr in addresses]
        log.info("Creating %d url groups" % len(url_groups))
        for group in url_groups:
            self.protocol.start(group)


class FeedStream(PollingDataStream):
    """
    If you expose your feed widget on the moksha.widget entry point,
    then Moksha will automatically handle polling it.  Upon new entries,
    AMQP messages will be sent to the `feeds.$URL` queue.
    """
    #frequency = timedelta(minutes=15)
    frequency = 5 # seconds
    running = False

    def poll(self):
        """ Poll all known feeds.

        - Iterate over all feeds in our global moksha feed cache..
            :Warning: the MokshaHub will not use this unless both it and the
                      Moksha WSGI app are using the same `feed_cache` database.

        - Keep feed caches fresh.

        - Send messages to topics for new entries
            `feed.$NAME` topic ?
            `tag.category
        """
        # @@ Only run once... for testing purposes
        if self.running:
            print "Feed streamer  already running"
            return
        self.running = True

        log.debug('FeedStream.poll()')
        feeds = map(lambda x: x.strip(), file('feeds.txt').readlines())
        feeds = [(feed, '') for feed in feeds]
        f = FeederFactory()
        f.start(addresses=feeds)
        return

    def stop(self):
        feed_storage.close()
        super(FeedStream, self).stop()

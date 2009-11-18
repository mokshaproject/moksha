# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from sqlalchemy import or_

from moksha.lib.base import Controller
from moksha.lib.helpers import defaultdict

#from moksha.model import DBSession
from moksha.apps.knowledge.model import Fact, Entity, with_characteristic, DBSession

class RootController(Controller):

    @expose('json')
    def index(self):
        #snake = Entity(u'snake')
        #snake[u'family'] = u'Python'
        #DBSession.add(snake)
        #DBSession.flush()
        num = DBSession.query(Entity).count()
        topics = defaultdict(list)
        for entity in DBSession.query(Entity).all():
                topics[entity.name] = None
        #        topics[entity.name] = entity.facts
        return dict(num=num, topics=topics)

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

from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation, comparable_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from moksha.model import metadata, DBSession, DeclarativeBase
from moksha.model.vertical import (PolymorphicVerticalProperty,
                                   VerticalPropertyDictMixin)


class Fact(PolymorphicVerticalProperty, DeclarativeBase):
    __tablename__ = 'facts'

    id = Column(Integer, ForeignKey('entities.id'), primary_key=True)
    key = Column(Unicode(64), primary_key=True)
    type_ = Column(Unicode(16), default=None)
    int_value = Column(Integer, default=None)
    char_value = Column(UnicodeText, default=None)
    boolean_value = Column(Boolean, default=None)
    datetime_value = Column(DateTime, default=None)

    value = comparable_property(PolymorphicVerticalProperty.Comparator,
                                PolymorphicVerticalProperty.value)

    type_map = {
        int: (u'integer', 'int_value'),
        unicode: (u'char', 'char_value'),
        bool: (u'boolean', 'boolean_value'),
        datetime: (u'datetime', 'datetime_value'),
        type(None): (None, None),
        }

with_characteristic = lambda key, value: and_(Fact.key==key, Fact.value==value)


class Entity(VerticalPropertyDictMixin, DeclarativeBase):
    """An entity.

    Entity facts are available via the 'facts' property or by using
    dict-like accessors on an Entity instance::

      apple = Entity('apple')
      apple['color'] = 'red'
      # or, equivalently:
      apple.facts['color'] = Fact('color', 'red')
    """
    __tablename__ = 'entities'
    _property_type = Fact
    _property_mapping = 'facts'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(100))

    facts = relation(Fact, backref='entity',
                     collection_class=attribute_mapped_collection('key'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    @classmethod
    def by_name(cls, name):
        """A class method that permits to search entities
        based on their name attribute.
        """
        return DBSession.query(cls).filter(cls.name==name).first()

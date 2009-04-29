# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Luke Macken <lmacken@redhat.com>

import logging
import sqlalchemy
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation, comparable_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from moksha.model.hook import MokshaHookMapperExtension
from moksha.model import metadata, DBSession, DeclarativeBase
from moksha.model.vertical import (PolymorphicVerticalProperty,
                                   VerticalPropertyDictMixin)

moksha_mapper_extension = MokshaHookMapperExtension()

class Fact(PolymorphicVerticalProperty, DeclarativeBase):
    """ A polymorphic-valued vertical table property """
    __tablename__ = 'facts'
    __mapper_args__ = {'extension': moksha_mapper_extension}

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
        str: (u'char', 'char_value'),
        unicode: (u'char', 'char_value'),
        bool: (u'boolean', 'boolean_value'),
        datetime: (u'datetime', 'datetime_value'),
        type(None): (None, None),
        }

with_characteristic = lambda key, value: and_(Fact.key==key, Fact.value==value)


class Entity(VerticalPropertyDictMixin, DeclarativeBase):
    """ An entity.

    Entity facts are available via the 'facts' property or by using
    dict-like accessors on an Entity instance::

      apple = Entity('apple')
      apple['color'] = 'red'
      # or, equivalently:
      apple.facts['color'] = Fact('color', 'red')
    """
    __tablename__ = 'entities'
    __mapper_args__ = {'extension': moksha_mapper_extension}
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

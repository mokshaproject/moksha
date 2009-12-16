# -*- coding: utf-8 -*-
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
# Copyright 2008-2009, Red Hat, Inc.
"""
:mod:`moksha.apps.knowledge.model` -- The Moksha Polymorphic Vertical Adjacency Tree Model
==========================================================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection

from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation, comparable_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from vertical import PolymorphicVerticalProperty, VerticalPropertyDictMixin

from moksha.model import metadata, DeclarativeBase, DBSession


class Fact(PolymorphicVerticalProperty, DeclarativeBase):
    """ A polymorphic-valued vertical table property """
    __tablename__ = 'moksha_facts'

    id = Column(Integer, ForeignKey('moksha_entities.id'), primary_key=True)
    key = Column(Unicode(64), primary_key=True)
    type_ = Column(Unicode(16), default=None)
    int_value = Column(Integer, default=None)
    char_value = Column(UnicodeText, default=None)
    boolean_value = Column(Boolean, default=None)
    datetime_value = Column(DateTime, default=None)
    list_value = Column(PickleType, default=None)
    dict_value = Column(PickleType, default=None)

    value = comparable_property(PolymorphicVerticalProperty.Comparator,
                                PolymorphicVerticalProperty.value)

    type_map = {
        int: (u'integer', 'int_value'),
        str: (u'char', 'char_value'),
        unicode: (u'char', 'char_value'),
        bool: (u'boolean', 'boolean_value'),
        datetime: (u'datetime', 'datetime_value'),
        list: (u'list', 'list_value'),
        dict: (u'dict', 'dict_value'),
        type(None): (None, None),
        }

with_characteristic = lambda key, value: and_(Fact.key==key, Fact.value==value)


class Entity(VerticalPropertyDictMixin, DeclarativeBase):
    """ An polymorphic entity.

    Entity facts are available via the 'facts' property or by using
    dict-like accessors on an Entity instance::

      apple = Entity('apple')
      apple['color'] = 'red'
      # or, equivalently:
      apple.facts['color'] = Fact('color', 'red')

    This Entity is also an adjacency tree.  Meaning, every entity
    can have a `parent` and zero or more `children`.
    """
    __tablename__ = 'moksha_entities'
    _property_type = Fact
    _property_mapping = 'facts'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(UnicodeText, nullable=False)

    facts = relation(Fact, backref='entity',
                     collection_class=attribute_mapped_collection('key'))

    # Adjacency tree properties
    #id = Column(Integer, Sequence('moksha_tree_id_seq', optional=True), primary_key=True)
    parent_id = Column(Integer, ForeignKey('moksha_entities.id'), nullable=True)

    children = relation('Entity', cascade="all",
                        backref=backref("parent", remote_side="Entity.id"),
                        collection_class=attribute_mapped_collection('name'),
                        lazy=False, join_depth=3)

    def __init__(self, name=None):
        self.name = name

    @classmethod
    def by_name(cls, name):
        """A class method that permits to search entities
        based on their name attribute.
        """
        return DBSession.query(cls).filter(cls.name==name).first()

    # Adjacency-tree methods
    def append(self, node):
        if isinstance(node, basestring):
            node = Entity(node)
        node.parent = self
        self.children[node.name] = node

    def __repr__(self):
        return self._getstring(0, False)

    def __str__(self):
        return self._getstring(0, False)

    def _getstring(self, level, expand = False):
        s = ('  ' * level) + "%s (%s,%s, %d)" % (
            self.name, self.id,self.parent_id,id(self)) + '\n'
        if expand:
            s += ''.join([n._getstring(level+1, True)
                          for n in self.children.values()])
        return s

    def print_nodes(self):
        return self._getstring(0, True)

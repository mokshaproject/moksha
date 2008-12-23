=======================
Moksha's Database Model
=======================

:Status: Under development

By default, Moksha aims to provide a default model to facilitate community interaction and knowledge cultivation.

Entity & Fact Model
-------------------

Moksha contains a generic model that can be used to store arbitrary entities
that have dynamic properties.  This model can be used or extended by any
Moksha application.  The data is stored in a polymorphic-valued vertical
table, and can be utilized as a normal Python dictionary.

Creating and manipulating Entities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> import transaction
    >>> from moksha.model import Entity, with_characteristic, DBSession
    >>> snake = Entity(u'snake')
    >>> snake[u'family'] = u'Python'
    >>> snake[u'venomous'] = False
    >>> DBSession.add(snake)
    >>> transaction.commit()

Querying entities by name
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> python = Entity.by_name(u'Python')


Querying entities by facts
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> snakes = (DBSession.query(Entity).
    ...           filter(or_(Entity.facts.any(
    ...                        with_characteristic(u'venomous', False)),
    ...                      not_(Entity.facts.any(Fact.key == u'venomous'))))).
    ...                      all()
    ...

Querying facts for certain entity characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> snakes = (DBSession.query(Fact).
    ...           filter(with_characteristic(u'venomous', False))).all()
    ...

Creating a dict-like polymorphic-valued vertical table
------------------------------------------------------

Moksha provides a :mod:`moksha.model.vertical` module that makes it easy to
define polymorphic-valued `vertical database <http://en.wikipedia.org/wiki/Partition_(database)>`_ models, using `SQLAlchemy <http://sqlalchemy.org>`_.  A good example of this is
the Entity/Fact model described above.

.. code-block:: python

    from datetime import datetime
    from sqlalchemy import *
    from sqlalchemy.orm import relation, comparable_property
    from sqlalchemy.orm.collections import attribute_mapped_collection
    from moksha.model import metadata, DBSession, DeclarativeBase
    from moksha.model.vertical import (PolymorphicVerticalProperty,
                                       VerticalPropertyDictMixin)

    class Fact(PolymorphicVerticalProperty, DeclarativeBase):
        """ A polymorphic-valued vertical table property """
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
        __tablename__ = 'entities'
        _property_type = Fact
        _property_mapping = 'facts'

        id = Column(Integer, autoincrement=True, primary_key=True)
        name = Column(Unicode(100))

        facts = relation(Fact, backref='entity',
                         collection_class=attribute_mapped_collection('key'))

        def __init__(self, name):
            self.name = name

        @classmethod
        def by_name(cls, name):
            return DBSession.query(cls).filter(cls.name==name).first()

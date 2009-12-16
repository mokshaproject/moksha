# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from sqlalchemy import or_
from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller, EditFormFiller
from sprox.formbase import AddRecordForm, EditableForm
from tw.core import WidgetsList
from tw.forms import TableForm, TextField, CalendarDatePicker, SingleSelectField, TextArea
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator
from repoze.what.predicates import has_permission

from moksha import model
#from moksha.model import DBSession, metadata
from moksha.lib.base import Controller
from moksha.lib.helpers import defaultdict
from moksha.apps.knowledge.model import Fact, Entity, with_characteristic, DBSession

#class EntityForm(TableForm):
#    class fields(WidgetsList):
#        name = TextField(validator=NotEmpty)
        #description = TextArea(attrs=dict(rows=3, cols=25))
        #release_date = CalendarDatePicker(validator=DateConverter())
        #genrechoices = ((1,"action"),
        #                 (2,"animation"),
        #                 (3,"comedy"),
        #                 (4,"documentary"),
        #                 (5,"drama"),
        #                 (6,"sci-fi"))
        #genre = SingleSelectField(options=genrechoices)

#then, we create an instance of this form
#movie_add_form = MovieForm("create_movie_form")
#
#

class EntityTable(TableBase):
    __model__ = Entity
entity_table = EntityTable(DBSession)

class EntityTableFiller(TableFiller):
    __model__ = Entity
entity_table_filler = EntityTableFiller(DBSession)

class EntityAddForm(AddRecordForm):
    __model__ = Entity
    __omit_fields__ = ['id', 'parent_id', 'facts', 'children']
entity_add_form = EntityAddForm(DBSession)

class EntityController(CrudRestController):
    requires = has_permission('manager')

    model = Entity
    #table = entity_table
    #table_filler = entity_table_filler
    #new_form = entity_add_form

    @expose('mako:moksha.apps.knowledge.templates.get_all')
    def get_all(self, *args, **kw):
        return super(EntityController, self).get_all(*args, **kw)

    @expose('mako:moksha.apps.knowledge.templates.new')
    def new(self, *args, **kw):
        return super(EntityController, self).new(*args, **kw)

    @expose('mako:moksha.apps.knowledge.templates.edit')
    def edit(self, *args, **kw):
        return super(EntityController, self).edit(*args, **kw)

    #@expose()
    #def post(self, **kw):
    #    print "EntityController.post(%s)" % locals()
    #    return super(EntityController, self).post(**kw)

    class new_form_type(AddRecordForm):
        __model__ = Entity
        __omit_fields__ = ['id', 'parent_id']

    class edit_form_type(EditableForm):
        __model__ = Entity
        __omit_fields__ = ['id', 'parent_id']

    class edit_filler_type(EditFormFiller):
        __model__ = Entity
        __omit_fields__ = ['id', 'parent_id']

    class table_type(TableBase):
        __model__ = Entity
        __omit_fields__ = ['id', 'parent_id']

    class table_filler_type(TableFiller):
        __model__ = Entity
        __omit_fields__ = ['id', 'parent_id']
        __xml_fields__ = ['children', 'facts']

        def children(self, entity):
            return ', '.join([child.name for child in entity.children])

        def facts(self, entity, *args, **kw):
            #print "facts(%s)"% locals()
            for fact in entity.facts:
                print fact
            return entity.name

class RootController(Controller):
    entities = EntityController(DBSession)

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

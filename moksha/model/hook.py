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
import pkg_resources

from sqlalchemy.orm.interfaces import MapperExtension

log = logging.getLogger(__name__)

class Hook(object):
    """ The parent Hook class """
    def after_insert(self, instance):
        pass
    def after_update(self, instance):
        pass
    def after_delete(self, instance):
        pass


class MokshaHookMapperExtension(MapperExtension):
    """
    This is a SQLAlchemy MapperExtension that handles loading up all of the
    moksha hooks, and running them when new objects are inserted, updated,
    and deleted from the model.
    """
    hooks = {'after_insert': [], 'after_update': [], 'after_delete': []}

    def __init__(self):
        super(MokshaHookMapperExtension, self).__init__()
        for hook_entry in pkg_resources.iter_entry_points('moksha.hook'):
            log.info('Loading %s hook' % hook_entry.name)
            hook_class = hook_entry.load()
            self.hooks[hook_entry.name].append(hook_class())

    def after_insert(self, mapper, connection, instance):
        for hook in self.hooks['after_insert']:
            hook.after_insert(instance)
        return sqlalchemy.orm.EXT_CONTINUE

    def after_update(self, mapper, connection, instance):
        for hook in self.hooks['after_update']:
            hook.after_update(instance)
        return sqlalchemy.orm.EXT_CONTINUE

    def after_delete(self, mapper, connection, instance):
        for hook in self.hooks['after_delete']:
            hook.after_delete(instance)
        return sqlalchemy.orm.EXT_CONTINUE

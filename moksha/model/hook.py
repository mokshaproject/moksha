# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

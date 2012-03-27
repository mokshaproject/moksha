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

"""Setup the moksha application"""
import logging
import transaction

from tg import config
from paste.deploy import appconfig

from moksha.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup moksha here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from moksha import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    u = model.User()
    u.user_name = u'manager'
    u.display_name = u'Example manager'
    u.email_address = u'manager@somedomain.com'
    u.password = u'managepass'

    model.DBSession.add(u)

    g = model.Group()
    g.group_name = u'managers'
    g.display_name = u'Managers Group'

    g.users.append(u)

    model.DBSession.add(g)

    p = model.Permission()
    p.permission_name = u'manage'
    p.description = u'This permission give an administrative right to the bearer'
    p.groups.append(g)

    model.DBSession.add(p)

    u1 = model.User()
    u1.user_name = u'editor'
    u1.display_name = u'Example editor'
    u1.email_address = u'editor@somedomain.com'
    u1.password = u'editpass'

    model.DBSession.add(u1)
    model.DBSession.flush()

    transaction.commit()
    print "Successfully setup"

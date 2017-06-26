from __future__ import print_function
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

import moksha.common.utils
import moksha.common.config
import re
import os
import logging

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

log = logging.getLogger(__name__)
scrub_filter = re.compile('[^_a-zA-Z0-9-]')


def get_moksha_config_path():
    """
    :returns: The path to Moksha's configuration file.
    """
    for config_path in ('.', '/etc/moksha/', __file__ + '/../../../'):
        for config_file in ('production.ini', 'development.ini'):
            cfg = os.path.join(os.path.abspath(config_path), config_file)
            if os.path.isfile(cfg):
                return cfg

    log.warning('No moksha configuration file found, make sure the '
             'controlling app is fully configured')

    return None


def get_moksha_dev_config():
    fname = 'development.ini'
    cfgs = [
        os.path.join(os.path.abspath(__file__ + '/../../../'), fname),
        os.path.join(os.path.abspath(__file__ + '/../../../../'), fname),
        os.path.join(os.getcwd(), fname),
        '/etc/moksha/%s' % fname,
    ]
    for cfg in cfgs:
        if os.path.isfile(cfg):
            return cfg
    log.warning("Cannot find configuration in %r" % cfgs)


def get_moksha_appconfig():
    """ Return the appconfig of Moksha """
    return appconfig('config:' + get_moksha_config_path())


def appconfig(config_path):
    """ Our own reimplementation of paste.deploy.appconfig """

    if config_path.startswith('config:'):
        config_path = config_path[7:]

    here = os.path.abspath(os.path.dirname(config_path))
    parser = moksha.common.config.EnvironmentConfigParser({"here": here})
    parser.read(filenames=[config_path])
    try:
        return dict(parser.items('app:main'))
    except configparser.NoSectionError:
        for section in parser.sections():
            if section.startswith('app:'):
                print("Using %r" % section)
                return dict(parser.items(section))

        raise configparser.NoSectionError("Couldn't find app: section.")


def create_app_engine(app, config):
    """ Create a new SQLAlchemy engine for a given app """
    from sqlalchemy import create_engine
    return create_engine(config.get('app_db', 'sqlite:///%s.db' % app))

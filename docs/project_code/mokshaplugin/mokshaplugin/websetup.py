"""Setup the mokshaplugin application"""
import logging

import transaction
from paste.deploy import appconfig
from tg import config

from mokshaplugin.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup mokshaplugin here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from mokshaplugin import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)


    transaction.commit()
    print "Successfully setup"

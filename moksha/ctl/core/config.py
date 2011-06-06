""" Loading moksha-ctl config from file (and the defaults!) """

import os
import ConfigParser

def load_config(fname="~/.moksha/ctl.conf"):
    """ Load a config file into a dictionary and return it """

    # Defaults
    config_d = {
        'VENV' : 'moksha',
        'APPS_DIR' : 'moksha/apps',
    }

    config = ConfigParser.ConfigParser()

    fname = os.path.expanduser(fname)
    if not os.path.exists(fname):
        raise ValueError, "No such file %s" % fname

    print "Reading config from", fname
    with open(fname) as f:
        config.readfp(f)

    if not config.has_section('moksha'):
        raise ValueError, "config file must have 'moksha' section"

    # Check for required fields
    if not config.has_option('moksha', 'SRC_DIR'):
        raise ValueError, "%s must have a SRC_DIR"

    # Extract all defined fields
    for key in ['SRC_DIR', 'VENV', 'APPS_DIR']:
        if config.has_option('moksha', key):
            config_d[key] = config.get('moksha', key)

    return config_d

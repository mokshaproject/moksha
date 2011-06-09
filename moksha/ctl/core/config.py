""" Loading moksha-ctl config from file (and the defaults!) """

import os
import ConfigParser


def load_config(fname="~/.moksha/ctl.conf"):
    """ Load a config file into a dictionary and return it """

    # Defaults
    config_d = {
        'VENV': 'moksha',
        'APPS_DIR': 'moksha/apps',
        'SRC_DIR': os.getcwd(),
    }

    config = ConfigParser.ConfigParser()

    fname = os.path.expanduser(fname)
    if os.path.exists(fname):
        print "Reading config from", fname
        with open(fname) as f:
            config.readfp(f)

        if config.has_section('moksha'):
            # Extract all defined fields
            for key in ['SRC_DIR', 'VENV', 'APPS_DIR']:
                if config.has_option('moksha', key):
                    config_d[key] = config.get('moksha', key)

    return config_d

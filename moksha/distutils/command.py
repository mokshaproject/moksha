
import os
import tg

from tg import config
from paste.deploy import appconfig

import tw2.core.command


def find_moksha_config():
    # Check for config files in the following locations
    possible_locations = [os.getcwd(), '/etc/moksha/']

    # Furthermore, look for these config filenames first
    preferred_names = ['build.ini', 'production.ini', 'development.ini']

    for location in possible_locations:
        filenames = [f for f in os.listdir(location) if f.endswith('.ini')]

        for preferred_name in preferred_names:
            if preferred_name in filenames:
                return os.path.join(location, preferred_name)

    return None


def load_moksha_config():
    filename = find_moksha_config()

    if not filename:
        print "Couldn't find a valid config file."
        sys.exit(1)

    print "Using", filename
    config = appconfig('config:%s' % filename)

    # Export our newly loaded config back to tg for the rest of
    # moksha to consume.
    tg.config = config
    return config

# If 'moksha' doesn't show up anywhere, we likely haven't loaded any config.
if not any(['moksha' in key for key in config.keys()]):
    config = load_moksha_config()

archive_moksha_resources = tw2.core.command.archive_tw2_resources

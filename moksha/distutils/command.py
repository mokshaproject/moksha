
import os
import tg
from tg import config
from paste.deploy import appconfig
from paste.deploy.converters import asbool

if not any(['moksha' in key for key in config.keys()]):
    config = None
    for guess in ['production.ini', 'development.ini']:
        try:
            config = appconfig('config:%s' % guess, relative_to=os.getcwd())
            print "Found", guess
            break
        except OSError as e:
            print str(e)

    if not config:
        print "Couldn't find a valid config file."
        sys.exit(1)

    tg.config = config


if asbool(config.get('moksha.use_tw2', False)):
    import tw2.core.command
    Parent = tw2.core.command.archive_tw2_resources
else:
    import tw.core.command
    Parent = tw.core.command.archive_tw_resources

class archive_moksha_resources(Parent):
    pass

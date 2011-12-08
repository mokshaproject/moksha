
import os
import tg
from tg import config
from paste.deploy import appconfig
from paste.deploy.converters import asbool

# If 'moksha' doesn't show up anywhere, we likely haven't loaded any config.
if not any(['moksha' in key for key in config.keys()]):

    # Try a couple guesses at where a config file might live.
    config = None
    for guess in ['production.ini', 'development.ini']:
        try:
            config = appconfig('config:%s' % guess, relative_to=os.getcwd())
            print "Found", guess
            break
        except OSError as e:
            print str(e)

    # If none of them worked, then we quit.
    if not config:
        print "Couldn't find a valid config file."
        sys.exit(1)

    # Otherwise, export our newly loaded config back to tg for the rest of
    # moksha to consume.  This is the crux -- moksha widgets need to know
    # whether to load as tw1 widgets or as tw2 widgets when they're slated to
    # have their resources archived.
    tg.config = config


if asbool(config.get('moksha.use_tw2', False)):
    import tw2.core.command
    Parent = tw2.core.command.archive_tw2_resources
else:
    import tw.core.command
    Parent = tw.core.command.archive_tw_resources

class archive_moksha_resources(Parent):
    pass

from tg.configuration import AppConfig, Bunch
import moksha
from moksha import model
from moksha.lib import app_globals, helpers

base_config = AppConfig()
base_config.package = moksha

# Set the default renderer
base_config.default_renderer = 'mako'
base_config.renderers = []
base_config.renderers.append('mako') 

# @@ This is necessary at the moment.
base_config.use_legacy_renderer = True

# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = moksha.model
base_config.DBSession = moksha.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
base_config.sa_auth.user_class = model.User
base_config.sa_auth.group_class = model.Group
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for 
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

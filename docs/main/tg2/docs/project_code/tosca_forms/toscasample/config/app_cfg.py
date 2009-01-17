from tg.configuration import AppConfig, Bunch
import toscasample
from toscasample import model
from toscasample.lib import app_globals, helpers

base_config = AppConfig()
base_config.renderers = []

base_config.package = toscasample

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi') 

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = toscasample.model
base_config.DBSession = toscasample.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# set a default hashing mechanism for the auth system
# this makes sure the passwords are not stored in clear-text
# inside the database. Choices are "md5", "sha1" or "salted_sha1"
base_config.sa_auth.password_encryption_method = "salted_sha1"

# override this if you would like to provide a different who plugin for 
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

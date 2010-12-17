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

from tg.configuration import AppConfig, Bunch
import moksha
from moksha import model
from moksha.lib import app_globals, helpers

base_config = AppConfig()
base_config.package = moksha

# Set the default renderer
base_config.default_renderer = 'mako'
base_config.renderers = []
base_config.renderers.append('genshi') 
base_config.renderers.append('mako') 
base_config.use_dotted_templatenames = True

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

# set a default hashing mechanism for the auth system
# this makes sure the passwords are not stored in clear-text
# inside the database. Choices are "md5", "sha1" or "salted_sha1"
base_config.sa_auth.password_encryption_method = "salted_sha1"
base_config.sa_auth.cookie_secret = "/\\/\\0|<5|-|4"

# override this if you would like to provide a different who plugin for 
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'

# Add Moksha's CSRF protection middleware by default
from moksha.middleware.csrf import CSRFMetadataProvider
base_config.sa_auth.mdproviders = [('csrfmd', CSRFMetadataProvider())]

# To enable the repoze.profile middleware.
# After surfing around, navigate to /__profile__ to view results.
base_config.profile = False

# Enable repoze.squeeze resource squeezing middleware
base_config.squeeze = False

from moksha import shutdown
base_config.call_on_shutdown.append(shutdown)

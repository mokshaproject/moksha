from tg.configuration import AppConfig, Bunch
import mokshaplugin
from mokshaplugin import model
from mokshaplugin.lib import app_globals, helpers

base_config = AppConfig()
base_config.renderers = []

base_config.package = mokshaplugin

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi') 

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = mokshaplugin.model
base_config.DBSession = mokshaplugin.model.DBSession


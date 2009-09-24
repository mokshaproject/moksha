import os
from paste.deploy import loadapp
cfg_path = os.path.join(os.path.dirname(__file__), '..', 'development.ini')
application = loadapp('config:' + cfg_path)

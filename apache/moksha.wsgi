import os, sys
sys.path.append('/srv/moksha')
os.environ['PYTHON_EGG_CACHE'] = '/srv/moksha/.python-eggs'

#sys.stdout = sys.stderr

from paste.deploy import loadapp

application = loadapp('config:/srv/moksha/development.ini')

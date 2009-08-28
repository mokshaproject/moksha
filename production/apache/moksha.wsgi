#import sys
#import os
#sys.path.append('/srv/moksha')
#os.environ['PYTHON_EGG_CACHE'] = '/srv/moksha/.python-eggs'
#sys.stdout = sys.stderr

import __main__
__main__.__requires__ = 'SQLAlchemy>=0.5'
import pkg_resources 
pkg_resources.require("SQLAlchemy>=0.5")
import sqlalchemy

from paste.deploy import loadapp
application = loadapp('config:/etc/moksha/production.ini')

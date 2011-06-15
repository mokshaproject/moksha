from tg import config
from paste.deploy.converters import asbool

import tw.api
from tw.jquery import jquery_js

tw1_jquery_json_js = tw.api.JSLink(
    modname=__name__,
    filename='static/jquery.json.js',
    javascript=[jquery_js])

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    jquery_json_js = tw1_jquery_json_js

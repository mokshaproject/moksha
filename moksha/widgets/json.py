from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

tw1_jquery_json_js = tw.api.JSLink(
    modname=__name__,
    filename='static/jquery.json.js',
    javascript=[tw.jquery.jquery_js])

tw2_jquery_json_js = twc.JSLink(
    modname=__name__,
    filename='static/jquery.json.js',
    resources=[tw2.jquery.jquery_js])

if asbool(config.get('moksha.use_tw2', False)):
    jquery_json_js = tw2_jquery_json_js
else:
    jquery_json_js = tw1_jquery_json_js

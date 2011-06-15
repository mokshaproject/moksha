from tg import config
from paste.deploy.converters import asbool

import tw.api
from tw.jquery import jquery_js

tw1_jquery_jgrowl_js = tw.api.JSLink(
    'jquery_jgrowl_js',
    filename='static/jquery.jgrowl.js',
    javascript=[jquery_js],
    modname=__name__)
tw1_jquery_jgrowl_css = tw.api.CSSLink(
    'jquery_jgrowl_css',
    filename='static/jquery.jgrowl.css',
    modname=__name__)


class TW1MokshaNotificationWidget(tw.api.Widget):
    javascript = [tw1_jquery_jgrowl_js]
    css = [tw1_jquery_jgrowl_css]


if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    MokshaNotificationWidget = TW1MokshaNotificationWidget


moksha_notify = MokshaNotificationWidget('moksha_notify')

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

tw1_jquery_jgrowl_js = tw.api.JSLink(
    'jquery_jgrowl_js',
    filename='static/jquery.jgrowl.js',
    javascript=[tw.jquery.jquery_js],
    modname=__name__)
tw1_jquery_jgrowl_css = tw.api.CSSLink(
    'jquery_jgrowl_css',
    filename='static/jquery.jgrowl.css',
    modname=__name__)


class TW1MokshaNotificationWidget(tw.api.Widget):
    javascript = [tw1_jquery_jgrowl_js]
    css = [tw1_jquery_jgrowl_css]


tw2_jquery_jgrowl_js = twc.JSLink(
    id='jquery_jgrowl_js',
    filename='static/jquery.jgrowl.js',
    resources=[tw2.jquery.jquery_js],
    modname=__name__)
tw2_jquery_jgrowl_css = twc.JSLink(
    id='jquery_jgrowl_css',
    filename='static/jquery.jgrowl.css',
    modname=__name__)


class TW2MokshaNotificationWidget(twc.Widget):
    resources = [tw2_jquery_jgrowl_js, tw2_jquery_jgrowl_css]


if asbool(config.get('moksha.use_tw2', False)):
    MokshaNotificationWidget = TW2MokshaNotificationWidget
    jquery_jgrowl_js = tw2_jquery_jgrowl_js
    jquery_jgrowl_css = tw2_jquery_jgrowl_css
    moksha_notify = MokshaNotificationWidget(id='moksha_notify')
else:
    MokshaNotificationWidget = TW1MokshaNotificationWidget
    jquery_jgrowl_js = tw1_jquery_jgrowl_js
    jquery_jgrowl_css = tw1_jquery_jgrowl_css
    moksha_notify = MokshaNotificationWidget('moksha_notify')

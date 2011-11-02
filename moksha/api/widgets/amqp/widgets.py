from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw2.core as twc

tw1_jsio_js = tw.api.JSLink(
    filename='static/jsio/jsio.js',
    modname=__name__)

tw1_amqp_resources = tw.api.Link(
    filename='static/',
    modname=__name__)

tw2_jsio_js = twc.JSLink(
    filename='static/jsio/jsio.js',
    modname=__name__)

tw2_amqp_resources=twc.DirLink(
    filename='static/',
    modname=__name__)


if asbool(config.get('moksha.use_tw2', False)):
    amqp_resources = tw2_amqp_resources
    jsio_js = tw2_jsio_js
else:
    amqp_resources = tw1_amqp_resources
    jsio_js = tw1_jsio_js

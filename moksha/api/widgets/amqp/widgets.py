from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw2.core as twc

tw1_kamaloka_protocol_js = tw.api.JSLink(
    filename='static/amqp.protocol.js',
    modname=__name__)

tw1_kamaloka_protocol_0_10_js = tw.api.JSLink(
    filename='static/amqp.protocol_0_10.js',
    javascript=[tw1_kamaloka_protocol_js],
    modname=__name__)

tw1_kamaloka_qpid_js = tw.api.JSLink(
    filename='static/qpid_amqp.js',
    javascript=[tw1_kamaloka_protocol_0_10_js],
    modname=__name__)

tw2_kamaloka_protocol_js = twc.JSLink(
    filename='static/amqp.protocol.js',
    modname=__name__)

tw2_kamaloka_protocol_0_10_js = twc.JSLink(
    filename='static/amqp.protocol_0_10.js',
    resources=[tw2_kamaloka_protocol_js],
    modname=__name__)

tw2_kamaloka_qpid_js = twc.JSLink(
    filename='static/qpid_amqp.js',
    resources=[tw2_kamaloka_protocol_0_10_js],
    modname=__name__)

if asbool(config.get('moksha.use_tw2', False)):
    kamaloka_protocol_js = tw2_kamaloka_protocol_js
    kamaloka_protocol_0_10_js = tw2_kamaloka_protocol_0_10_js
    kamaloka_qpid_js = tw2_kamaloka_qpid_js
else:
    kamaloka_protocol_js = tw1_kamaloka_protocol_js
    kamaloka_protocol_0_10_js = tw1_kamaloka_protocol_0_10_js
    kamaloka_qpid_js = tw1_kamaloka_qpid_js

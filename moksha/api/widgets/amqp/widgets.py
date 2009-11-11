from tw.api import JSLink

kamaloka_protocol_js = JSLink(filename='static/amqp.protocol.js', modname=__name__)

kamaloka_protocol_0_10_js = JSLink(filename='static/amqp.protocol_0_10.js',
                                   javascript=[kamaloka_protocol_js],
                                   modname=__name__)

kamaloka_qpid_js = JSLink(filename='static/qpid_amqp.js',
                          javascript=[kamaloka_protocol_0_10_js],
                          modname=__name__)



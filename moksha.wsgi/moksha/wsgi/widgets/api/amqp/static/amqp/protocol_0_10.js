/*********************************************************
 * Generated AMQP lowlevel protocol bindings
 *
 * We put this under the namespace
 * amqp.protocol_<vermajor>_<version_minor> to
 * seperate out the generated bindings from the high level
 * bindings.
 *
 * Also note we use a notation that is easier for generated
 * output but not as readable as hand written code.  Every
 * section outputs a complete javascript block.
 *********************************************************/

(function(){

jsio('import Class, bind');
jsio('import jsio.logging');
jsio('from jsio.interfaces import Protocol');
jsio('import amqp.protocol');
jsio('from amqp.protocol import DefaultsClass');



/******* Module Properties ***********/
var BUILD_DATE = 'Wednesday, 02. November 2011 10:00AM';
exports.BUILD_DATE = BUILD_DATE;

var None = null;
var protocol_header = 'AMQP';
protocol_header += String.fromCharCode(1, 1, 0, 10);

var logger = jsio.logging.getLogger('AmqpProtocol0.10' );

var CONTROL_SEG_TYPE = 0;
var COMMAND_SEG_TYPE = 1;
var HEADER_SEG_TYPE = 2;
var BODY_SEG_TYPE = 3;

var version = {
    major: 0,
    minor: 10,
    toString: function(){return "0.10"}
};

var default_port = 5672;

// The minimum size (in bytes) which can be     agreed upon as the maximum frame size.
var MIN_MAX_FRAME_SIZE = 4096;


var amqp_types = {};
var amqp_typecodes = {};
var amqp_classes = {};
var amqp_classcodes = {};

/******* Module Methods ***********/
var lookup_type = function(typecode) {
    return amqp_typecodes[typecode];
}

var lookup_class = function(classcode) {
    return amqp_classcodes[classcode];
}

var get_header = function() {
    return protocol_header;
}

var guess_type = function(value) {
    if (typeof(value) == 'number') {
        var sn = value.toString(10);
        var absv = Math.abs(value);
        if (vn.indexOf('.') == -1) {
            if (absv < (1 << 7)) {
                return new amqp_types['int8'](value);
            } else if (absv < (1 << 15)) {
                return new amqp_types['int16'](value);
            } else if (absv < (1 << 31)) {
                return new amqp_types['int32'](value);
            } else if (absv < (1 << 63)) {
                return new amqp_types['int64'](value);
            }
        } else {
            // send as a double
            return new amqp_types['double'](value);
        }
    } else if (typeof(value) == 'string') {
        var l = value.length;
        if (l < (1 << 8))
            return new amqp_types['str8'](value);
        else if (l < (1 << 16))
            return new amqp_types['str16'](value);
    } else if (typeof(value) == 'object' && value.encode) {
        return value;
    } else {
        throw "Can not guess the value of '" + value + "' not yet handled in guess_type";
    }
}

/******** Marshaler classes ***********/
var Marshaler = Class(function() {
     this.code = null;

     this.init = function(value, is_type_encoded) {
         if (typeof(is_type_encoded) == 'undefined')
             is_type_encoded = true;

         this._value = value;
         this._is_type_encoded = is_type_encoded;
     };

     this.set_value = function(value) {
         this._value = value;
     };

     this.decode = function(assembly) {

     };

     this.encode = function(assembly) {

     };

     // container types need to find the marshalers to decode their children
    this.lookup_type = lookup_type;
    this.guess_type = guess_type;

    this.lookup_class = lookup_class;
});

var TypeMarshaler = Class(Marshaler, function(supr) {
    this.code = null;

    this.decode = function(assembly, decoder, size) {
        return decoder.call(this, assembly, size);
    };

    this.encode = function(assembly, encoder, size) {
        var code = null;
        if (this._is_type_encoded)
            code = this.code;

        encoder.call(this, assembly, code, size, this._value);
    };



});

var StructMarshaler = Class(Marshaler, function(supr) {
    this.name = 'undefined_struct';
    this.code = null;
    this.pack_size = 0;
    this.size = 0;
    this.parent_class = null;
    this.is_struct = true;

    this.decode = function(assembly) {
        var result = {};
        // read size octet for session.header packing flags
        var pack_size = this.pack_size;
        var packing_flags = 0;
        for (var i=0; i < pack_size; i++)
            packing_flags += new amqp_types['int8']().decode(assembly) << (i*8);

        for (var i in this.fields) {
            if (packing_flags & this.fields[i][3]) {
                var name = this.fields[i][0];
                var type_class = this.fields[i][1];
                var type_obj = new type_class();
                var size = 0;

                // if this is a struct we need to get the encoded size of the
                // struct first
                if (type_obj.is_struct)
                    size = amqp.protocol.decode_int(assembly, type_obj.size);

                result[name] = type_obj.decode(assembly);
            }
        }

        return result;
    }

    this.encode = function(assembly) {
        // we need to get the size of the struct
        var struct_assembly = new amqp.protocol.Assembly({});
        var values = this._value;

        var packing_flags = 0;
        for (var i in this.fields) {
            var name = this.fields[i][0];
            var type_class = this.fields[i][1];
            var v = values[name];

            if (typeof(v) != 'undefined') {
                // special case bits
                if(type_class == amqp_types['bit']) {
                    if (v)
                        packing_flags += (1 << i);
                } else {
                    packing_flags += (1 << i);
                    new type_class(v, false).encode(struct_assembly);
                }
            }
        }

        var header = '';
        if(this._is_type_encoded)
            header += String.fromCharCode(this.parent_class.code, this.code)

        var pf = amqp.protocol.int_to_bytestr(packing_flags, this.pack_size);
        for (var i=pf.length - 1; i >= 0; i--)
            header += pf[i];

        struct_assembly.prepend(header);

        var size = struct_assembly.get_size(false);
        var enc_size = amqp.protocol.int_to_bytestr(size, 4);
        struct_assembly.prepend(enc_size);
        assembly.write(struct_assembly.get_data());

    }
});

var HeaderSegmentMarshaler = Class(Marshaler, function(supr) {
    this.encode = function(assembly, is_first_segment, is_last_segment, channel) {
        var payload_assembly = new amqp.protocol.Assembly({});
        var value = this._value;
        for(var id in value) {
            var s = this.parent_class.structs[id];
            if(s)
                new s(value[id]).encode(payload_assembly);
        }

        // find the size of our data structure
        var payload_data = payload_assembly.get_data();

        var frame = new Frame({assembly: assembly,
                                   payload: payload_data,
                                   parsed_data: {
                                       frame_format_version: 0,
                                       is_first_segment: is_first_segment,
                                       is_last_segment: is_last_segment,
                                       is_first_frame: true,
                                       is_last_frame: true,
                                       segment_type: HEADER_SEG_TYPE,
                                       track: 1,
                                       channel: channel,
                                    }
                                   });
        frame.encode();
        return frame;
    }
});

var BodySegmentMarshaler = Class(Marshaler, function(supr) {
    this.encode = function (assembly, is_first_segment, is_last_segment, channel) {
        var frame = new Frame({assembly: assembly,
                               payload: this._value,
                               parsed_data: {
                                       frame_format_version: 0,
                                       is_first_segment: is_first_segment,
                                       is_last_segment: is_last_segment,
                                       is_first_frame: true,
                                       is_last_frame: true,
                                       segment_type: BODY_SEG_TYPE,
                                       track: 1,
                                       channel: channel
                                    }
                                });
        frame.encode();
        return frame;
    }
});

var MessageMarshaler = Class(Marshaler, function(supr) {
    this.seg_type = null;
    this.code = null;
    this.name = null;
    this.parent_class = null;

    this.init = function (value) {
        supr(this, 'init', [value]);
    }
});

var ControlMessageMarshaler = Class(MessageMarshaler, function (supr) {
    this.seg_type = CONTROL_SEG_TYPE;
    this.name = 'unknown_control',

    this.init = function (value) {
        supr(this, 'init', [value]);
    };

    this.decode = function(assembly) {
        var result = {};
        var packing_flags = new amqp_types['int8']().decode(assembly);
        var packing_flags2 = new amqp_types['int8']().decode(assembly) << 8;
        packing_flags += packing_flags2;

        var fields = this.fields;
        for (i in fields) {
            if (packing_flags & fields[i][3]) {
                var name = fields[i][0];
                var type_class = fields[i][1];
                result[name] = new type_class().decode(assembly);
            }
        }

        return result;
    };

    this.encode = function(assembly) {
        var packing_flags = 0;
        var fields = this.fields;
        var values = this._value;

        for (var i in fields) {
            var name = fields[i][0];
            var type_class = fields[i][1];
            var required = fields[i][2];
            var v = values[name];

            if (typeof(v) != 'undefined') {
                // special case bits
                if(type_class == amqp_types['bit']) {
                    if (v)
                        packing_flags += (1 << i);
                } else {
                    packing_flags += (1 << i);
                    new type_class(v, false).encode(assembly);
                }
            } else if (required) {
                throw "Parameter " + name + " is required for message" + this.parent_class.name + "." + this.name;
            }
        }

        var header = String.fromCharCode(this.parent_class.code, this.code)
        var pf = amqp.protocol.int_to_bytestr(packing_flags, 2);
        for (var i=pf.length - 1; i >= 0; i--)
            header += pf[i];

        assembly.prepend(header);

    }

});

var CommandMessageMarshaler = Class(ControlMessageMarshaler, function(supr) {
    this.seg_type = COMMAND_SEG_TYPE;

    this.init = function(value) {
        supr(this, 'init', [value]);
    };

    this.decode = function(assembly) {
        // read one octet for session.header packing flags
        var session_packing_flags = new amqp_types['int8']().decode(assembly);

        // we discard session struct right now
        var session_struct = null;
        if (session_packing_flags)
            session_struct = new amqp_types['int8']().decode(assembly);

        var result = supr(this, 'decode', [assembly]);
        return result;
    };

    this.encode = function(assembly, values) {
        var packing_flags = 0;
        var values = this._value;

        for (var i in this.fields) {
            var name = this.fields[i][0];
            var type = this.fields[i][1];
            var v = values[name];

            if (typeof(v) != 'undefined') {
                // special case bits
                if(type == amqp_types['bit']) {
                    if (v)
                        packing_flags += (1 << i);
                } else {
                    packing_flags += (1 << i);
                    new type(v, false).encode(assembly);
                }
            }
        }

        var segments = this.segments;
        if (typeof(segments) != 'undefined') {
            // prepare segments for encoding
            var available_segments = [];
            for (var i in segments) {
                var seg = segments[i];
                var v = values[seg.name];
                if (typeof(v) != 'undefined' || v != null)
                    available_segments.push(seg);
            }

            // let upper frames know they need to indicate there are more segments
            if (available_segments.length) {
                assembly.set_metadata('has_multiple_segments', true);
                var frames = [];
                assembly.set_metadata('segment_frames', frames);
                // encode segments
                for (var i in available_segments) {
                    var segment_assembly = new amqp.protocol.Assembly({});
                    var seg = available_segments[i];
                    var v = values[seg.name];
                    // right now we only send on channel 0
                    var channel = 0;
                    var frame = new seg.marshaler(v).encode(segment_assembly, 0, i==available_segments.length-1, channel);
                    frames.push(frame);
                }
            }
        }

        var header = String.fromCharCode(this.parent_class.code, this.code)
        // FIXME: session headers are version dependent so we should
        //        do this in a generate_session_header method
        if (values['sync']) {
            // request sync call
            var sync_flags = amqp.protocol.int_to_bytestr(0x01,1);
            // add twice since both packing flags and values = 1
            header += sync_flags;
            header += sync_flags;
        } else {
            // only add packing flag = 0
            var sync_flags = amqp.protocol.int_to_bytestr(0x00,1);
            header += sync_flags;
            header += sync_flags;
        }
        var pf = amqp.protocol.int_to_bytestr(packing_flags, 2);
        for (var i=pf.length - 1; i >= 0; i--)
            header += pf[i];

        assembly.prepend(header);
    }
});

var Message = Class(amqp.protocol.Message, function (supr) {

    this.decode_next_segment = function() {
        supr(this, 'decode_next_segment');
        var payload_size = this.assembly.get_metadata('payload_size');

        switch(this._current_segment_type) {
            case CONTROL_SEG_TYPE:
            case COMMAND_SEG_TYPE:
                this.decode_cls();
                break;

            case HEADER_SEG_TYPE:
                this.decode_header(payload_size);
                break;

            case BODY_SEG_TYPE:
                this.decode_body(payload_size);
                break;

            default:
                throw "Invalid segment type encountered"
        };
    };

    this.decode_cls = function() {
        var a = this.assembly;
        var cls_code = this.set('class_code', new amqp_types['uint8']().decode(a));
        var message_code = this.set('message_code', new amqp_types['uint8']().decode(a));
        this.class_code = cls_code;
        this.code = message_code;

        var cls = amqp_classcodes[cls_code];
        this.parent_class = cls;
        this.class_name = this.parent_class.name;

        if (typeof(cls) === 'undefined')
            throw('Class code (' + cls_code + ') is invalid. \
                  This usually happens when a previous message was decoded \
                  incorrectly or it contained a type which is not supported \
                  yet');

        var method = cls.message_codes[message_code];
        var msg = new method();
        this.marshaler = msg;
        this.name = msg.name;

        var results = msg.decode(a);
        for (var k in results)
            this.set(k, results[k]);
    }

    this.decode_header = function(payload_size) {
        var a = this.assembly;
        var header = {};

        do {
            var struct_size = new amqp_types['uint32']().decode(a);
            var cls_code = this.set('class_code', new amqp_types['uint8']().decode(a));
            var header_code = this.set('message_code', new amqp_types['uint8']().decode(a));

            var cls = amqp_classcodes[cls_code];
            this.parent_class = cls;

            if (typeof(cls) === 'undefined')
                throw('Class code (' + cls_code + ') is invalid. \
                  This usually happens when a previous message was decoded \
                  incorrectly or it contained a type which is not supported \
                  yet');

            var st = new cls.struct_codes[header_code]();
            var values = st.decode(a);
            var key = st.name;
            header[key] = values;
            payload_size = payload_size - (struct_size + 4);
        } while (payload_size > 0);

        this.set('_header', header);
    }

    this.decode_body = function(size) {
        var a = this.assembly;
        var data = a.read_byte(size);
        this.set('_body', data);
    }
});

var Frame = Class(DefaultsClass, function (supr) {
    var defaults = {
        assembly: null,
        parsed_data: {},
        contains_header: false,
        payload: ''
    }

    this.init = function(options) {
        supr(this, 'init', [options, defaults]);
        if (!this.assembly)
            this.assembly = new amqp.protocol.Assembly({});
    }

    this.decode = function() {
        var assembly = this.assembly;

        // Parse the header
        if (this.contains_header)
            this.set('header', amqp.protocol.decode_header(assembly));

        // now the Frame
        this.set('frame_format_version', assembly.read_bit(2));
        assembly.read_bit(2);
        this.set('is_first_segment', assembly.read_bit(1));
        this.set('is_last_segment', assembly.read_bit(1));
        this.set('is_first_frame', assembly.read_bit(1));
        this.set('is_last_frame', assembly.read_bit(1));
        this.set('segment_type', new amqp_types['uint8']().decode(assembly));
        this.set('frame_size', new amqp_types['uint16']().decode(assembly));
        assembly.read_byte(1);
        assembly.read_bit(4);
        this.set('track', assembly.read_bit(4));
        this.set('channel', new amqp_types['uint16']().decode(assembly));
        assembly.read_byte(4);
        var payload_size = this.get('frame_size') - 12; // frame size - header size
        this.set('payload_size', payload_size);
    };

    this.encode = function() {
        var a = this.assembly;

        // Add the header
        if(this.contains_header)
            a.write(get_header());

        // now the Frame
        var ffv = this.get('frame_format_version');
        var next_byte = ffv << 6;

        //next two bits are reserved while we add the rest of the bits
        if(this.get('is_first_segment'))
            next_byte += 1 << 3;
        if(this.get('is_last_segment'))
            next_byte += 1 << 2;
        if(this.get('is_first_frame'))
            next_byte += 1 << 1;
        if(this.get('is_last_frame'))
            next_byte += 1;

        a.write(String.fromCharCode(next_byte));
        var st = amqp.protocol.int_to_bytestr(this.get('segment_type'), 1);
        a.write(st);

        // set the frame size which is the size of the header +
        // size field (2) + padding byte (1) + track field (1) +
        // channel field (2) + padding bytes(4) + size of payload
        var frame_size = a.get_size(false) + 10 + this.payload.length;
        var fs = amqp.protocol.int_to_bytestr(frame_size, 2);
        a.write(fs);
        a.write(String.fromCharCode(0));
        var t = amqp.protocol.int_to_bytestr(this.get('track'), 1);
        a.write(t);
        var ch = amqp.protocol.int_to_bytestr(this.get('channel'), 2);
        a.write(ch);
        a.write(String.fromCharCode(0,0,0,0));
        a.write(this.payload);
    }

    this.get = function(key) {
        return this.parsed_data[key];
    }

    this.set = function(key, value) {
        this.parsed_data[key] = value;
        return value;
    }

    this.get_assembly = function() {
        return this.assembly;
    }

    this.get_data = function() {
        return this.assembly.get_data();
    }
});

/******* driver classes ********/
var DEFAULT_DURABILITY = true;
var CREDIT_FLOW_MODE = 0;
var WINDOW_FLOW_MODE = 0;
var BYTE_FLOW = 0;
var MESSAGE_FLOW = 1;

var MessagingHandshakeDriver = Class(function() {
    this.init = function(handler, session, address) {
        this._handler = handler;
        var query_results = [];

        var declare = function() {
            var opts = address.options;
            var props = opts['node-properties'];
            if (typeof(props) == 'undefined')
                props = {};

            durable = props['durable'];
            if (typeof(durable) == 'undefined')
                durable = DEFAULT_DURABILITY;

            var node_type = props['type'];
            if(typeof(node_type) == 'undefined')
                node_type = 'queue';

            xprops = props['x-properties'];
            if (typeof(xprops) == 'undefined')
                xprops = {};

            var bindings = xprops['bindings'];
            if (typeof(bindings) == 'undefined')
                bindings = [];

            var declare_args = protocol.deep_copy_defaults(xargs);
            delete declare_args['bindings'];

            var msgs = [];
            var subtype = null;
            if (node_type == 'topic') {
                msgs.push(amqp_classes.Exchange.declare({exchange: name,
                                                         durable: durable,
                                                         arguments: declare_args}));
                /* FIXME: python bindings make it look like this can be something
                          other than topic */
                subtype = 'topic';
            } else if (node_type == 'queue') {
                msgs.push(amqp_classes.Queue.declare({queue: name,
                                                     durable:durable,
                                                     arguments: declare_args}));
                for(b in bindings) {
                    var baddr = new protocol.AddressParser(bindings[b]);
                    msg.push(amqp_classes.Exchange.bind({queue: name,
                                                         exchange: baddr.name,
                                                         binding_key: baddr.subject,
                                                         arguments: badder.options
                                                        }));
                }
            } else {
                throw('unrecognized type, must be topic or queue: ' + node_type);
            }

            for (m in msgs) {
                session.send(msgs[m]);
            }

            handler.do_link(node_type, subtype);

        };

        var do_resolved = function(query_results) {
            var er = query_results[0];
            var qr = query_results[1];

            if(er.not_found && !qr.queue && handler.check_policy(address.options.create)) {
                declare();
            } else if (qr.queue) {
                handler.do_link('queue');
            } else {
                handler.do_link('topic', er.type);
            }
        };

        var exchange_query_results = function(results) {
            query_results.push(results);
            return true;
        };

        var queue_query_results = function(results) {
            query_results.push(results);
            do_resolved(query_results);
            return true;
        };

        /* query the name to see if a node exists */
        session.Exchange('query', {name: address.name});
        session._conn._conn_driver.subscribe('execution',
                                             'result',
                                             null,
                                             exchange_query_results,
                                             true);

        session.Queue('query', {name: address.name});
        session._conn._conn_driver.subscribe('execution',
                                             'result',
                                             null,
                                             queue_query_results,
                                             true);
    }
});

var Sender = Class(amqp.protocol.Sender, function(supr) {
    this.init = function(session, index, source, options) {
        supr(this, 'init', [session, index, source, options]);
        this._ready = false;
        this.driver = new MessagingHandshakeDriver(this,
                                                   session,
                                                   this.addr);
    };

    this._construct_transfer = function(payload, msg_props) {
        if (!msg_props)
            msg_props = {};

        var msg = amqp_classes.Message.transfer({destination: this._exchange,
                                                 _body: payload,
                                                 _header: {
                                                     delivery_properties: {
                                                         routing_key: this._routing_key,
                                                     },
                                                     message_properties: msg_props
                                                 }
                                                });
        return msg;
    };

    this._dispatch_one = function(msg) {
       this._sess._sess_driver.send(msg);
    };

    this.check_policy = function(policy) {
        if(policy == 'always' || policy == 'sender')
            return true;

        return false;
    };

    this.do_link = function(type, subtype) {
        if (type == 'topic') {
            this._exchange = this.addr.name;
            this._routing_key = this.addr.subject;
        } else if (type == 'queue') {
            this._exchange = '';
            this._routing_key = this.addr.name;
        }

        this._ready = true;
        this.sync();
    };
});

var Receiver = Class(amqp.protocol.Receiver, function(supr) {
    this.init = function(session, index, source, options) {
        supr(this, 'init', [session, index, source, options]);
        this._ready = false;
        this.driver = new MessagingHandshakeDriver(this,
                                                   session,
                                                   this.addr);
    };

    this.grant = function() {
        if (!this._grant_pending)
            return;

        this._grant_pending = false;
        this._sess.Message('flow',
                           {destination: this.destination,
                            unit: BYTE_FLOW,
                            value: this._capacity});

        this._sess.Message('flow',
                           {destination: this.destination,
                            unit: MESSAGE_FLOW,
                            value: this._capacity});

    };

    this.check_policy = function(policy) {
        if(policy == 'always' || policy == 'receiver')
            return true;

        return false;
    };

    this.do_link = function(type, subtype) {
        if (type == 'topic') {
            this._queue = this._sess.name + '.' + this._index;
            this._sess.Queue('declare', {queue: this._queue,
                                         durable: DEFAULT_DURABILITY,
                                         exclusive: true,
                                         auto_delete: true});

            var f = this.addr.subject_to_filter();
            if (this.addr.options.filter) {
                if (f)
                    throw "Filter '" +  this.addr.options.filter + "' and subject '"+ this.addr.subject + "' are both set.  Only one should be set";

                f = this.addr.options.filter;
            }

            if (!f && subtype == 'topic')
                f = '#';

            this._sess.Exchange('bind', {exchange: this.addr.name,
                                         queue: this._queue,
                                         binding_key: f});



        } else if (type == 'queue') {
            this._queue = this.addr.name;
        }

        this._sess.Message('subscribe', {queue: this._queue,
                                         destination: this.destination});

        this._sess.Message('set_flow_mode', {destination: this.destination,
                                             flow_mode: CREDIT_FLOW_MODE});

        this.grant();
    };
});


var Session = Class(amqp.protocol.DefaultsClass, function(supr) {
    var defaults = {
        uuid: null,
        connection: null
    };

    this.init = function(options) {
        supr(this, 'init', [options, defaults]);
        this.name = options.uuid;
        this._conn = options.connection;
        this._defered = [];
        this._ready = false;
        this._outgoing = [];

        var _me = this;

        // setup the session handshake sequence
        // FIXME: Handle already existing connections
        this._conn.subscribe('session',
                             'attached',
                             0,
                             function(frame) {
                                 var msg = frame.get('msg');
                                 var flush = amqp_classes.Session.flush({expected: false,
                                                                         confirmed: false,
                                                                         completed: true});

                                 _me._conn.send(flush);
                             },
                             true
                            );

        this._conn.subscribe('session',
                             'completed',
                             0,
                             function(frame) {
                                 var msg = frame.get('msg');
                                 var known_completed = amqp_classes.Session.known_completed({});

                                 _me._conn.send(known_completed);
                                 var request_timeout = amqp_classes.Session.request_timeout({timeout: 400});

                                 _me._conn.send(request_timeout);
                             },
                             true
                            );

        this._conn.subscribe('session',
                             'timeout',
                             0,
                             function(frame) {
                                 var msg = frame.get('msg');
                                 var command_point = amqp_classes.Session.command_point({command_id: 0,
                                                                                         command_offset:0});

                                 _me._conn.send(command_point);

                                 for(var i=0; i<_me._defered.length; i++)
                                     _me._conn.send(_me._defered[i]);

                                 _me._ready = true;
                             },
                             true
                            );

        var attach = amqp_classes.Session.attach({name: this.name});
        this._conn.send(attach);

    };

    this.Receiver = Receiver;
    this.Sender = Sender;

    this.send = function(msg) {
        if (this._ready)
            this._conn.send(msg);
        else
            this._defered.push(msg);
    };

    this.Queue = function(command_name, params) {
        var queue_msg = amqp_classes.Queue[command_name](params);
        this.send(queue_msg);
    };

    this.Exchange = function(command_name, params) {
        var ex_msg = amqp_classes.Exchange[command_name](params);
        this.send(ex_msg);
    };

    this.Message = function(command_name, params) {
        var message_msg = amqp_classes.Message[command_name](params);
        this.send(message_msg);
    };

    this.link_receiver = function(recv) {
        this.Exchange('query',{'name': this.name});
        sst.write_query(QueueQuery(name), do_action)
    }
});

var Connection = Class(DefaultsClass, function(supr) {
    var defaults = {
        host: 'localhost',
        port: 9000,
        username: '',
        password: '',
        send_hook: function() {},
        recive_hook: function() {},
        socket_cls: null,
        channel_max: 32767,
        max_frame_size: 65535,
        heartbeat_min: 0,
        heartbeat_max: 120
    }

    this.statecode = {
        CLOSED: 0,
        CONNECTING: 1,
        HANDSHAKE_STAGE_1: 2,
        CONNECTED: 3,
        NEGOTIATED: 4
    }

    this.init = function(options) {
        supr(this, 'init', [options, defaults]);
        this._prenegotiation_msg_queue = [];

        this._socket = new this.socket_cls();
        this.state = this.statecode.CLOSED;
        this._dispatch_table = {};
        this._incomming = {};

        this._socket.onopen = bind(this, function() {
            console.log('connection opened!');

            // Handshake
            this.state = this.statecode.HANDSHAKE_STAGE_1;
            protocol_header = this.get_header();

            this._raw_send(protocol_header);
        });

        var process_data = function(data) {
            var sc = this.statecode;
            var assembly = null;

            if (data instanceof amqp.protocol.Assembly)
                assembly = data;
            else
                assembly = new amqp.protocol.Assembly({data: data});

            assembly.mark_start(); // debug metadata

            switch(this.state) {
                case sc.HANDSHAKE_STAGE_1:
                    this.state = sc.CONNECTED;
                    var frame = new Frame({assembly: assembly,
                                           contains_header: true});
                    frame.decode();

                    var track = frame.get('track');
                    var type = frame.get('segment_type');

                    if (track != 0)
                        throw "Expecting a control frame but recived a command during stage 1 of the handshake";
                    if (type != 0)
                        throw "Recived the wrong control code during stage 1 of the handshake";

                    this._process_frame(frame,
                                        bind(this,
                                             this._process_handshake_stage_1));

                    break;

                case sc.CONNECTED:
                case sc.NEGOTIATED:
                    // dispatch from here
                    var frame = new Frame({assembly: assembly,
                                           contains_header: false});

                    frame.decode();

                    this._process_frame(frame,
                                        bind(this,
                                             this._process_dispatch));

                    break;

                default:
                    throw "State code 0x" + _me.state.toString(16) + " is not implemented by amqp.Connecton";

            }


            // check for more frames
            if (!assembly.eof())
                process_data.call(this, assembly);

        };

        this._socket.onread = bind(this, process_data);

        this._socket.onclose = function(code) {
            console.log('Connection Closed [' + code + ']');
        };

        /* implicitly start when created */
        this.start();
    };

    this._process_frame = function(frame,
                                  complete_cb) {

        // Process is outlined in the flowchart in
        // docs/misc/frame_decoding.dia

        var is_first_frame = frame.get('is_first_frame');
        var is_last_frame = frame.get('is_last_frame');
        var is_first_segment = frame.get('is_first_segment');
        var is_last_segment = frame.get('is_last_segment');
        var channel = frame.get('channel');
        var track = frame.get('track');
        var id = channel + '.' + track;

        var msg = this._incomming[id];
        if (is_first_frame && is_first_segment) {
            if (msg)
                throw "Error: Message collision - channel " + channel + " track " + track + " already has a partial message in the queue";

            msg = new Message({});
            this._incomming[id] = msg;
        }

        msg.add_frame(frame);

        if (is_last_frame) {
            msg.decode_next_segment();
            if (is_last_segment) {
                complete_cb(msg);
                delete this._incomming[id];
            }
        }
    };

    this._process_handshake_stage_1 = function(msg) {
        if (this.recive_hook)
            this.recive_hook(msg);

        var srv_properties = msg.get('server_properties');
        var mechanisms = msg.get('mechanisms');
        var locales = msg.get('locales');

        // send start-ok response
        // FIXME: Support other auth mechanisms

        var start_ok_msg = amqp_classes.Connection.start_ok({
                client_properties: {
                    product: 'qpid kamaloka javascript client',
                    platform: navigator.userAgent
                },
                mechanism: 'ANONYMOUS',
                locale: 'en_US',
                response: ''
        });

        this.subscribe('connection',
                       'tune',
                       0,
                       this.handle_tune_cmd);

        this._send_handshake(start_ok_msg);
    };

    this._process_dispatch = function(msg) {
        if (this.recive_hook)
            this.recive_hook(msg);

        var cls_code = msg.get_class_code();
        var message_code = msg.get_code();
        var track = msg.get('track');
        var channel = msg.get('channel');
        var id = '';

        id = cls_code + '.' + message_code;

        var callbacks = this._dispatch_table[id];
        if (callbacks) {
            var discard_pile = [];
            for (var i in callbacks) {
                var cb = callbacks[i][0];
                var discard = callbacks[i][1];
                var ch = callbacks[i][2];
                if (typeof(ch) != undefined && ch != null)
                    if (ch != channel) // we are looking for a specific channel
                        continue;

                if (discard)
                    delete callbacks[i];

                if (cb) {
                    var handled = cb.call(this, msg);
                    if (handled)
                        break;
                }
            }

        }
    };

    this.unsubscribe = function(id) {
         var callback_list = this._dispatch_table[id[0]];
         delete callback_list[id[1]];
    };

    this.subscribe = function (cls_name, msg_name, channel, callback, discard) {
        var cls = amqp_classes[cls_name];
        var cls_code = cls.code;
        var msg_code = cls.messages[msg_name.toUpperCase()];
        var id = cls_code + '.' + msg_code;
        var callback_list = this._dispatch_table[id];

        if (!callback_list)
            callback_list = []

        var index = callback_list.length;
        callback_list.push([callback, discard, channel]);

        this._dispatch_table[id] = callback_list;

        return [id, index];
    };

    this.get_state = function() {
        return this.state;
    };

    this.lookup_type = lookup_type;

    this.get_header = get_header;

    this.guess_type = guess_type;

    this._raw_send = function (msg) {
        this._socket.send(msg);
    };

    this.send = function(message, is_negotiating) {
        // queue messages if we are still negotiating
        if (!is_negotiating && !(this.state == this.statecode.NEGOTIATED)) {
            this._prenegotiation_msg_queue.push(message);
            return;
        }

        this._send(message);
    };

    this._send = function (message) {
        message.encode();

        // FIXME: break up if size is too big
        var size = message.get_size();
        var payload = message.get_data(size);
        var msg_type = message.get_type();
        var code = message.get_code();
        var cls_code = message.get_class_code();
        var segment_type = msg_type;
        var channel = 0;
        var track = msg_type;
        var has_multiple_segments = message.has_multiple_segments();
        var is_last_segment = !has_multiple_segments;

        // FIXME: get module version from the header info
        //        and work with segments and multiple frames
        var frame = new Frame({
            parsed_data: {
                frame_format_version: 0,
                is_first_segment: true,
                is_last_segment: is_last_segment,
                is_first_frame: true,
                is_last_frame: true,
                segment_type: segment_type, // control
                track: track,
                channel: channel,
                message_code: code,
                class_code: cls_code,
                msg: message
            },
            payload: payload
        });

        frame.encode();
        var data = frame.get_data();
        var debug_frames = [frame];
        if(has_multiple_segments) {
            var seg_frames = message.get_segment_frames();
            for (var i in seg_frames) {
                debug_frames.push(seg_frames[i]);
                var seg_data = seg_frames[i].get_data();
                data = data + seg_data;
            }
        }

        // FIXME: have message do the framing
        message._frames = debug_frames;

        this._raw_send(data);
        if (this.send_hook) {
            this.send_hook(message);
        }
    };

    this._send_handshake = this._send;

    this.start = function() {
        if (this.state != this.statecode.CLOSED)
            return;

        this.state = this.statecode.CONNECTING;
        this._socket.open(this.host, this.port, isBinary=true);
    };

    this.handle_tune_cmd = function (frame) {

        var channel_max = frame.get('channel_max');
        var max_frame_size = frame.get('max_frame_size');
        var heartbeat_min = frame.get('heartbeat_min');
        var heartbeat_max = frame.get('heartbeat_max');

        if (this.channel_max > channel_max)
            this.channel_max = channel_max;

        if (this.max_frame_size > max_frame_size)
            this.max_frame_size = max_frame_size;

        if (this.heartbeat_min > heartbeat_min)
            this.heartbeat_min = heartbeat_min;

        if (this.heartbeat_max > heartbeat_max)
            this.heartbeat_max = heartbeat_max;

        /* FIXME: allow setting and handling of heartbeat */
        var tune_ok_msg = amqp_classes.Connection.tune_ok({
            channel_max: this.channel_max,
            max_frame_size: this.max_frame_size
        });

        this._send_handshake(tune_ok_msg);

        this.subscribe('connection', 'open_ok', 0, this.handle_open_ok_cmd, true);
        var open_msg = amqp_classes.Connection.open({virtual_host:''});
        this._send_handshake(open_msg);
    };

    this.handle_open_ok_cmd = function (frame) {
        this.state = this.statecode.NEGOTIATED;
        for (var i = 0; i < this._prenegotiation_msg_queue.length; i++)
            this.send(this._prenegotiation_msg_queue[i]);
    };

    this.create_session = function(uuid) {
        var sess = new Session({uuid: uuid,
                                connection: this});

        return sess;
    };
});


/******* AMQP Protocol MetaData ********/

// octet of unspecified encoding
amqp_types['BIN8'] = 0x00;
amqp_types['bin8'] = Class(TypeMarshaler, function(s) {
    this.code = 0x00;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 1])};
});
amqp_typecodes[0x00] = amqp_types['bin8'];

// 8-bit signed integral value (-128 - 127)
amqp_types['INT8'] = 0x01;
amqp_types['int8'] = Class(TypeMarshaler, function(s) {
    this.code = 0x01;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_int, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_int, 1])};
});
amqp_typecodes[0x01] = amqp_types['int8'];

// 8-bit unsigned integral value (0 - 255)
amqp_types['UINT8'] = 0x02;
amqp_types['uint8'] = Class(TypeMarshaler, function(s) {
    this.code = 0x02;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_uint, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_uint, 1])};
});
amqp_typecodes[0x02] = amqp_types['uint8'];

// an iso-8859-15 character
amqp_types['CHAR'] = 0x04;
amqp_types['char'] = Class(TypeMarshaler, function(s) {
    this.code = 0x04;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 1])};
});
amqp_typecodes[0x04] = amqp_types['char'];

// boolean value (zero represents false, nonzero represents true)
amqp_types['BOOLEAN'] = 0x08;
amqp_types['boolean'] = Class(TypeMarshaler, function(s) {
    this.code = 0x08;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bool, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bool, 1])};
});
amqp_typecodes[0x08] = amqp_types['boolean'];

// two octets of unspecified binary encoding
amqp_types['BIN16'] = 0x10;
amqp_types['bin16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x10;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 2])};
});
amqp_typecodes[0x10] = amqp_types['bin16'];

// 16-bit signed integral value
amqp_types['INT16'] = 0x11;
amqp_types['int16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x11;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_int, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_int, 2])};
});
amqp_typecodes[0x11] = amqp_types['int16'];

// 16-bit unsigned integer
amqp_types['UINT16'] = 0x12;
amqp_types['uint16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x12;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_uint, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_uint, 2])};
});
amqp_typecodes[0x12] = amqp_types['uint16'];

// four octets of unspecified binary encoding
amqp_types['BIN32'] = 0x20;
amqp_types['bin32'] = Class(TypeMarshaler, function(s) {
    this.code = 0x20;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 4])};
});
amqp_typecodes[0x20] = amqp_types['bin32'];

// 32-bit signed integral value
amqp_types['INT32'] = 0x21;
amqp_types['int32'] = Class(TypeMarshaler, function(s) {
    this.code = 0x21;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_int, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_int, 4])};
});
amqp_typecodes[0x21] = amqp_types['int32'];

// 32-bit unsigned integral value
amqp_types['UINT32'] = 0x22;
amqp_types['uint32'] = Class(TypeMarshaler, function(s) {
    this.code = 0x22;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_uint, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_uint, 4])};
});
amqp_typecodes[0x22] = amqp_types['uint32'];

// single precision IEEE 754 32-bit floating point
amqp_types['FLOAT'] = 0x23;
amqp_types['float'] = Class(TypeMarshaler, function(s) {
    this.code = 0x23;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_float, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_float, 4])};
});
amqp_typecodes[0x23] = amqp_types['float'];

// single unicode character in UTF-32 encoding
amqp_types['CHAR_UTF32'] = 0x27;
amqp_types['char_utf32'] = Class(TypeMarshaler, function(s) {
    this.code = 0x27;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 4])};
});
amqp_typecodes[0x27] = amqp_types['char_utf32'];

// serial number defined in RFC-1982
amqp_types['SEQUENCE_NO'] = None;
amqp_types['sequence_no'] = Class(TypeMarshaler, function(s) {
    this.code = None;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_uint, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_uint, 4])};
});
amqp_typecodes[None] = amqp_types['sequence_no'];

// eight octets of unspecified binary encoding
amqp_types['BIN64'] = 0x30;
amqp_types['bin64'] = Class(TypeMarshaler, function(s) {
    this.code = 0x30;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 8])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 8])};
});
amqp_typecodes[0x30] = amqp_types['bin64'];

// 64-bit signed integral value
amqp_types['INT64'] = 0x31;
amqp_types['int64'] = Class(TypeMarshaler, function(s) {
    this.code = 0x31;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_int, 8])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_int, 8])};
});
amqp_typecodes[0x31] = amqp_types['int64'];

// 64-bit unsigned integral value
amqp_types['UINT64'] = 0x32;
amqp_types['uint64'] = Class(TypeMarshaler, function(s) {
    this.code = 0x32;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_uint, 8])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_uint, 8])};
});
amqp_typecodes[0x32] = amqp_types['uint64'];

// double precision IEEE 754 floating point
amqp_types['DOUBLE'] = 0x33;
amqp_types['double'] = Class(TypeMarshaler, function(s) {
    this.code = 0x33;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_float, 8])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_float, 8])};
});
amqp_typecodes[0x33] = amqp_types['double'];

// datetime in 64 bit POSIX time_t format
amqp_types['DATETIME'] = 0x38;
amqp_types['datetime'] = Class(TypeMarshaler, function(s) {
    this.code = 0x38;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_datetime, 8])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_datetime, 8])};
});
amqp_typecodes[0x38] = amqp_types['datetime'];

// sixteen octets of unspecified binary encoding
amqp_types['BIN128'] = 0x40;
amqp_types['bin128'] = Class(TypeMarshaler, function(s) {
    this.code = 0x40;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 16])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 16])};
});
amqp_typecodes[0x40] = amqp_types['bin128'];

// UUID (RFC-4122 section 4.1.2) - 16 octets
amqp_types['UUID'] = 0x48;
amqp_types['uuid'] = Class(TypeMarshaler, function(s) {
    this.code = 0x48;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 16])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 16])};
});
amqp_typecodes[0x48] = amqp_types['uuid'];

// thirty two octets of unspecified binary encoding
amqp_types['BIN256'] = 0x50;
amqp_types['bin256'] = Class(TypeMarshaler, function(s) {
    this.code = 0x50;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 32])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 32])};
});
amqp_typecodes[0x50] = amqp_types['bin256'];

// sixty four octets of unspecified binary encoding
amqp_types['BIN512'] = 0x60;
amqp_types['bin512'] = Class(TypeMarshaler, function(s) {
    this.code = 0x60;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 64])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 64])};
});
amqp_typecodes[0x60] = amqp_types['bin512'];

// one hundred and twenty eight octets of unspecified binary encoding
amqp_types['BIN1024'] = 0x70;
amqp_types['bin1024'] = Class(TypeMarshaler, function(s) {
    this.code = 0x70;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 128])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 128])};
});
amqp_typecodes[0x70] = amqp_types['bin1024'];

// up to 255 octets of opaque binary data
amqp_types['VBIN8'] = 0x80;
amqp_types['vbin8'] = Class(TypeMarshaler, function(s) {
    this.code = 0x80;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 1])};
});
amqp_typecodes[0x80] = amqp_types['vbin8'];

// up to 255 iso-8859-15 characters
amqp_types['STR8_LATIN'] = 0x84;
amqp_types['str8_latin'] = Class(TypeMarshaler, function(s) {
    this.code = 0x84;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 1])};
});
amqp_typecodes[0x84] = amqp_types['str8_latin'];

// up to 255 octets worth of UTF-8 unicode
amqp_types['STR8'] = 0x85;
amqp_types['str8'] = Class(TypeMarshaler, function(s) {
    this.code = 0x85;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 1])};
});
amqp_typecodes[0x85] = amqp_types['str8'];

// up to 255 octets worth of UTF-16 unicode
amqp_types['STR8_UTF16'] = 0x86;
amqp_types['str8_utf16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x86;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 1])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 1])};
});
amqp_typecodes[0x86] = amqp_types['str8_utf16'];

// up to 65535 octets of opaque binary data
amqp_types['VBIN16'] = 0x90;
amqp_types['vbin16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x90;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 2])};
});
amqp_typecodes[0x90] = amqp_types['vbin16'];

// up to 65535 iso-8859-15 characters
amqp_types['STR16_LATIN'] = 0x94;
amqp_types['str16_latin'] = Class(TypeMarshaler, function(s) {
    this.code = 0x94;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 2])};
});
amqp_typecodes[0x94] = amqp_types['str16_latin'];

// up to 65535 octets worth of UTF-8 unicode
amqp_types['STR16'] = 0x95;
amqp_types['str16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x95;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 2])};
});
amqp_typecodes[0x95] = amqp_types['str16'];

// up to 65535 octets worth of UTF-16 unicode
amqp_types['STR16_UTF16'] = 0x96;
amqp_types['str16_utf16'] = Class(TypeMarshaler, function(s) {
    this.code = 0x96;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 2])};
});
amqp_typecodes[0x96] = amqp_types['str16_utf16'];

// byte ranges within a 64-bit payload
amqp_types['BYTE_RANGES'] = None;
amqp_types['byte_ranges'] = Class(TypeMarshaler, function(s) {
    this.code = None;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 2])};
});
amqp_typecodes[None] = amqp_types['byte_ranges'];

// ranged set representation
amqp_types['SEQUENCE_SET'] = None;
amqp_types['sequence_set'] = Class(TypeMarshaler, function(s) {
    this.code = None;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_seq_set, 2])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_seq_set, 2])};
});
amqp_typecodes[None] = amqp_types['sequence_set'];

// up to 4294967295 octets of opaque binary data
amqp_types['VBIN32'] = 0xa0;
amqp_types['vbin32'] = Class(TypeMarshaler, function(s) {
    this.code = 0xa0;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_str, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_str, 4])};
});
amqp_typecodes[0xa0] = amqp_types['vbin32'];

// a mapping of keys to typed values
amqp_types['MAP'] = 0xa8;
amqp_types['map'] = Class(TypeMarshaler, function(s) {
    this.code = 0xa8;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_map, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_map, 4])};
});
amqp_typecodes[0xa8] = amqp_types['map'];

// a series of consecutive type-value pairs
amqp_types['LIST'] = 0xa9;
amqp_types['list'] = Class(TypeMarshaler, function(s) {
    this.code = 0xa9;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 4])};
});
amqp_typecodes[0xa9] = amqp_types['list'];

// a defined length collection of values of a single type
amqp_types['ARRAY'] = 0xaa;
amqp_types['array'] = Class(TypeMarshaler, function(s) {
    this.code = 0xaa;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_array, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_array, 4])};
});
amqp_typecodes[0xaa] = amqp_types['array'];

// a coded struct with a 32-bit size
amqp_types['STRUCT32'] = 0xab;
amqp_types['struct32'] = Class(TypeMarshaler, function(s) {
    this.code = 0xab;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_struct, 4])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_struct, 4])};
});
amqp_typecodes[0xab] = amqp_types['struct32'];

// five octets of unspecified binary encoding
amqp_types['BIN40'] = 0xc0;
amqp_types['bin40'] = Class(TypeMarshaler, function(s) {
    this.code = 0xc0;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 5])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 5])};
});
amqp_typecodes[0xc0] = amqp_types['bin40'];

// 32-bit decimal value (e.g. for use in financial values)
amqp_types['DEC32'] = 0xc8;
amqp_types['dec32'] = Class(TypeMarshaler, function(s) {
    this.code = 0xc8;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_dec, 5])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_dec, 5])};
});
amqp_typecodes[0xc8] = amqp_types['dec32'];

// nine octets of unspecified binary encoding
amqp_types['BIN72'] = 0xd0;
amqp_types['bin72'] = Class(TypeMarshaler, function(s) {
    this.code = 0xd0;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bin, 9])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bin, 9])};
});
amqp_typecodes[0xd0] = amqp_types['bin72'];

// 64-bit decimal value (e.g. for use in financial values)
amqp_types['DEC64'] = 0xd8;
amqp_types['dec64'] = Class(TypeMarshaler, function(s) {
    this.code = 0xd8;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_dec, 9])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_dec, 9])};
});
amqp_typecodes[0xd8] = amqp_types['dec64'];

// the void type
amqp_types['VOID'] = 0xf0;
amqp_types['void'] = Class(TypeMarshaler, function(s) {
    this.code = 0xf0;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_void, 0])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_void, 0])};
});
amqp_typecodes[0xf0] = amqp_types['void'];

// presence indicator
amqp_types['BIT'] = 0xf1;
amqp_types['bit'] = Class(TypeMarshaler, function(s) {
    this.code = 0xf1;
    this.decode = function(assembly) {return s(this, 'decode', [assembly, amqp.protocol.decode_bit, 0])};
    this.encode = function(assembly) {return s(this, 'encode', [assembly, amqp.protocol.encode_bit, 0])};
});
amqp_typecodes[0xf1] = amqp_types['bit'];


// work with connections
amqp_classes['CONNECTION'] = 0x1;
amqp_classes['connection'] = new function(){
    var this_class = this;
    this.code = 0x1;
    this.name = 'connection';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};



    // start connection negotiation
    this.messages['START'] = 0x1;
    this.messages['start'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'start';
        this.parent_class = this_class;
        this.fields = [];


        // server properties
        this.fields.push(['server_properties', amqp_types['map'], false, 1]);

        // available security mechanisms
        this.fields.push(['mechanisms', amqp_types['array'], true, 2]);

        // available message locales
        this.fields.push(['locales', amqp_types['array'], true, 4]);

    ;
    });
    this.message_codes[0x1] = this.messages['start'];

    // select security mechanism and locale
    this.messages['START_OK'] = 0x2;
    this.messages['start_ok'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'start_ok';
        this.parent_class = this_class;
        this.fields = [];


        // client properties
        this.fields.push(['client_properties', amqp_types['map'], false, 1]);

        // selected security mechanism
        this.fields.push(['mechanism', amqp_types['str8'], true, 2]);

        // security response data
        this.fields.push(['response', amqp_types['vbin32'], true, 4]);

        // selected message locale
        this.fields.push(['locale', amqp_types['str8'], true, 8]);

    ;
    });
    this.message_codes[0x2] = this.messages['start_ok'];

    // security mechanism challenge
    this.messages['SECURE'] = 0x3;
    this.messages['secure'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'secure';
        this.parent_class = this_class;
        this.fields = [];


        // security challenge data
        this.fields.push(['challenge', amqp_types['vbin32'], true, 1]);

    ;
    });
    this.message_codes[0x3] = this.messages['secure'];

    // security mechanism response
    this.messages['SECURE_OK'] = 0x4;
    this.messages['secure_ok'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'secure_ok';
        this.parent_class = this_class;
        this.fields = [];


        // security response data
        this.fields.push(['response', amqp_types['vbin32'], true, 1]);

    ;
    });
    this.message_codes[0x4] = this.messages['secure_ok'];

    // propose connection tuning parameters
    this.messages['TUNE'] = 0x5;
    this.messages['tune'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'tune';
        this.parent_class = this_class;
        this.fields = [];


        // proposed maximum channels
        this.fields.push(['channel_max', amqp_types['uint16'], false, 1]);

        // proposed maximum frame size
        this.fields.push(['max_frame_size', amqp_types['uint16'], false, 2]);

        // the minimum supported heartbeat delay
        this.fields.push(['heartbeat_min', amqp_types['uint16'], false, 4]);

        // the maximum supported heartbeat delay
        this.fields.push(['heartbeat_max', amqp_types['uint16'], false, 8]);

    ;
    });
    this.message_codes[0x5] = this.messages['tune'];

    // negotiate connection tuning parameters
    this.messages['TUNE_OK'] = 0x6;
    this.messages['tune_ok'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'tune_ok';
        this.parent_class = this_class;
        this.fields = [];


        // negotiated maximum channels
        this.fields.push(['channel_max', amqp_types['uint16'], true, 1]);

        // negotiated maximum frame size
        this.fields.push(['max_frame_size', amqp_types['uint16'], false, 2]);

        // negotiated heartbeat delay
        this.fields.push(['heartbeat', amqp_types['uint16'], false, 4]);

    ;
    });
    this.message_codes[0x6] = this.messages['tune_ok'];

    // open connection to virtual host
    this.messages['OPEN'] = 0x7;
    this.messages['open'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'open';
        this.parent_class = this_class;
        this.fields = [];


        // virtual host name
        this.fields.push(['virtual_host', amqp_types['str8'], true, 1]);

        // required capabilities
        this.fields.push(['capabilities', amqp_types['array'], false, 2]);

        // insist on connecting to server
        this.fields.push(['insist', amqp_types['bit'], false, 4]);

    ;
    });
    this.message_codes[0x7] = this.messages['open'];

    // signal that connection is ready
    this.messages['OPEN_OK'] = 0x8;
    this.messages['open_ok'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'open_ok';
        this.parent_class = this_class;
        this.fields = [];


        // alternate hosts which may be used in         the case of failure
        this.fields.push(['known_hosts', amqp_types['array'], false, 1]);

    ;
    });
    this.message_codes[0x8] = this.messages['open_ok'];

    // redirects client to other server
    this.messages['REDIRECT'] = 0x9;
    this.messages['redirect'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x9;
        this.name = 'redirect';
        this.parent_class = this_class;
        this.fields = [];


        // server to connect to
        this.fields.push(['host', amqp_types['str16'], true, 1]);

        // alternate hosts to try in case of         failure
        this.fields.push(['known_hosts', amqp_types['array'], false, 2]);

    ;
    });
    this.message_codes[0x9] = this.messages['redirect'];

    // indicates connection is still alive
    this.messages['HEARTBEAT'] = 0xa;
    this.messages['heartbeat'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xa;
        this.name = 'heartbeat';
        this.parent_class = this_class;
        this.fields = [];


    ;
    });
    this.message_codes[0xa] = this.messages['heartbeat'];

    // request a connection close
    this.messages['CLOSE'] = 0xb;
    this.messages['close'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xb;
        this.name = 'close';
        this.parent_class = this_class;
        this.fields = [];


        // the numeric reply code
        this.fields.push(['reply_code', amqp_types['uint16'], true, 1]);

        // the localized reply text
        this.fields.push(['reply_text', amqp_types['str8'], false, 2]);

    ;
    });
    this.message_codes[0xb] = this.messages['close'];

    // confirm a connection close
    this.messages['CLOSE_OK'] = 0xc;
    this.messages['close_ok'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xc;
        this.name = 'close_ok';
        this.parent_class = this_class;
        this.fields = [];


    ;
    });
    this.message_codes[0xc] = this.messages['close_ok'];


}();

amqp_classes['Connection'] = new function(){

    this.start = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['start'](),
                                          parsed_data: params});
    }

    this.start_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['start_ok'](),
                                          parsed_data: params});
    }

    this.secure = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['secure'](),
                                          parsed_data: params});
    }

    this.secure_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['secure_ok'](),
                                          parsed_data: params});
    }

    this.tune = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['tune'](),
                                          parsed_data: params});
    }

    this.tune_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['tune_ok'](),
                                          parsed_data: params});
    }

    this.open = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['open'](),
                                          parsed_data: params});
    }

    this.open_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['open_ok'](),
                                          parsed_data: params});
    }

    this.redirect = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['redirect'](),
                                          parsed_data: params});
    }

    this.heartbeat = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['heartbeat'](),
                                          parsed_data: params});
    }

    this.close = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['close'](),
                                          parsed_data: params});
    }

    this.close_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['connection'].messages['close_ok'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x1] = amqp_classes['connection'];

// session controls
amqp_classes['SESSION'] = 0x2;
amqp_classes['session'] = new function(){
    var this_class = this;
    this.code = 0x2;
    this.name = 'session';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['HEADER'] = 0;
    this.structs['header'] = Class(StructMarshaler, function(s) {
        this.code = 0;
        this.name = 'header';
        this.pack_size = 1;
        this.size = 1;
        this.parent_class = this_class;
        this.fields = [];

        // request notification of completion
        this.fields.push(['sync', amqp_types['bit'], false, 1]);

    ;
    });
    this.struct_codes[0] = this.structs['header'];

    this.structs['COMMAND_FRAGMENT'] = 0;
    this.structs['command_fragment'] = Class(StructMarshaler, function(s) {
        this.code = 0;
        this.name = 'command_fragment';
        this.pack_size = 0;
        this.size = 0;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['command_id', amqp_types['sequence_no'], true, 1]);

        // None
        this.fields.push(['byte_ranges', amqp_types['byte_ranges'], true, 2]);

    ;
    });
    this.struct_codes[0] = this.structs['command_fragment'];



    // attach to the named session
    this.messages['ATTACH'] = 0x1;
    this.messages['attach'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'attach';
        this.parent_class = this_class;
        this.fields = [];


        // the session name
        this.fields.push(['name', amqp_types['vbin16'], true, 1]);

        // force attachment to a busy session
        this.fields.push(['force', amqp_types['bit'], false, 2]);

    ;
    });
    this.message_codes[0x1] = this.messages['attach'];

    // confirm attachment to the named session
    this.messages['ATTACHED'] = 0x2;
    this.messages['attached'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'attached';
        this.parent_class = this_class;
        this.fields = [];


        // the session name
        this.fields.push(['name', amqp_types['vbin16'], true, 1]);

    ;
    });
    this.message_codes[0x2] = this.messages['attached'];

    // detach from the named session
    this.messages['DETACH'] = 0x3;
    this.messages['detach'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'detach';
        this.parent_class = this_class;
        this.fields = [];


        // the session name
        this.fields.push(['name', amqp_types['vbin16'], true, 1]);

    ;
    });
    this.message_codes[0x3] = this.messages['detach'];

    // confirm detachment from the named session
    this.messages['DETACHED'] = 0x4;
    this.messages['detached'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'detached';
        this.parent_class = this_class;
        this.fields = [];


        // the session name
        this.fields.push(['name', amqp_types['vbin16'], true, 1]);

        // the reason for detach
        this.fields.push(['code', amqp_types['uint8'], true, 2]);

    ;
    });
    this.message_codes[0x4] = this.messages['detached'];

    // requests the execution timeout be changed
    this.messages['REQUEST_TIMEOUT'] = 0x5;
    this.messages['request_timeout'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'request_timeout';
        this.parent_class = this_class;
        this.fields = [];


        // the requested timeout
        this.fields.push(['timeout', amqp_types['uint32'], false, 1]);

    ;
    });
    this.message_codes[0x5] = this.messages['request_timeout'];

    // the granted timeout
    this.messages['TIMEOUT'] = 0x6;
    this.messages['timeout'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'timeout';
        this.parent_class = this_class;
        this.fields = [];


        // the execution timeout
        this.fields.push(['timeout', amqp_types['uint32'], false, 1]);

    ;
    });
    this.message_codes[0x6] = this.messages['timeout'];

    // the command id and byte offset of subsequent data
    this.messages['COMMAND_POINT'] = 0x7;
    this.messages['command_point'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'command_point';
        this.parent_class = this_class;
        this.fields = [];


        // the command-id of the next command
        this.fields.push(['command_id', amqp_types['sequence_no'], true, 1]);

        // the byte offset within the command
        this.fields.push(['command_offset', amqp_types['uint64'], true, 2]);

    ;
    });
    this.message_codes[0x7] = this.messages['command_point'];

    // informs the peer of expected commands
    this.messages['EXPECTED'] = 0x8;
    this.messages['expected'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'expected';
        this.parent_class = this_class;
        this.fields = [];


        // expected commands
        this.fields.push(['commands', amqp_types['sequence_set'], true, 1]);

        // expected fragments
        this.fields.push(['fragments', amqp_types['array'], false, 2]);

    ;
    });
    this.message_codes[0x8] = this.messages['expected'];

    // notifies of confirmed commands
    this.messages['CONFIRMED'] = 0x9;
    this.messages['confirmed'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0x9;
        this.name = 'confirmed';
        this.parent_class = this_class;
        this.fields = [];


        // entirely confirmed commands
        this.fields.push(['commands', amqp_types['sequence_set'], false, 1]);

        // partially confirmed commands
        this.fields.push(['fragments', amqp_types['array'], false, 2]);

    ;
    });
    this.message_codes[0x9] = this.messages['confirmed'];

    // notifies of command completion
    this.messages['COMPLETED'] = 0xa;
    this.messages['completed'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xa;
        this.name = 'completed';
        this.parent_class = this_class;
        this.fields = [];


        // completed commands
        this.fields.push(['commands', amqp_types['sequence_set'], false, 1]);

        // None
        this.fields.push(['timely_reply', amqp_types['bit'], false, 2]);

    ;
    });
    this.message_codes[0xa] = this.messages['completed'];

    // Inform peer of which commands are known to be       completed
    this.messages['KNOWN_COMPLETED'] = 0xb;
    this.messages['known_completed'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xb;
        this.name = 'known_completed';
        this.parent_class = this_class;
        this.fields = [];


        // commands known to be complete
        this.fields.push(['commands', amqp_types['sequence_set'], false, 1]);

    ;
    });
    this.message_codes[0xb] = this.messages['known_completed'];

    // requests a session.completed
    this.messages['FLUSH'] = 0xc;
    this.messages['flush'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xc;
        this.name = 'flush';
        this.parent_class = this_class;
        this.fields = [];


        // request notification of expected commands
        this.fields.push(['expected', amqp_types['bit'], false, 1]);

        // request notification of confirmed commands
        this.fields.push(['confirmed', amqp_types['bit'], false, 2]);

        // request notification of completed commands
        this.fields.push(['completed', amqp_types['bit'], false, 4]);

    ;
    });
    this.message_codes[0xc] = this.messages['flush'];

    // indicates missing segments in the stream
    this.messages['GAP'] = 0xd;
    this.messages['gap'] = Class(ControlMessageMarshaler, function(s) {
        this.code = 0xd;
        this.name = 'gap';
        this.parent_class = this_class;
        this.fields = [];


        // None
        this.fields.push(['commands', amqp_types['sequence_set'], false, 1]);

    ;
    });
    this.message_codes[0xd] = this.messages['gap'];


}();

amqp_classes['Session'] = new function(){

    this.attach = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['attach'](),
                                          parsed_data: params});
    }

    this.attached = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['attached'](),
                                          parsed_data: params});
    }

    this.detach = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['detach'](),
                                          parsed_data: params});
    }

    this.detached = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['detached'](),
                                          parsed_data: params});
    }

    this.request_timeout = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['request_timeout'](),
                                          parsed_data: params});
    }

    this.timeout = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['timeout'](),
                                          parsed_data: params});
    }

    this.command_point = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['command_point'](),
                                          parsed_data: params});
    }

    this.expected = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['expected'](),
                                          parsed_data: params});
    }

    this.confirmed = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['confirmed'](),
                                          parsed_data: params});
    }

    this.completed = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['completed'](),
                                          parsed_data: params});
    }

    this.known_completed = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['known_completed'](),
                                          parsed_data: params});
    }

    this.flush = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['flush'](),
                                          parsed_data: params});
    }

    this.gap = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['session'].messages['gap'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x2] = amqp_classes['session'];

// execution commands
amqp_classes['EXECUTION'] = 0x3;
amqp_classes['execution'] = new function(){
    var this_class = this;
    this.code = 0x3;
    this.name = 'execution';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};



    // request notification of completion for issued commands
    this.messages['SYNC'] = 0x1;
    this.messages['sync'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'sync';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x1] = this.messages['sync'];

    // carries execution results
    this.messages['RESULT'] = 0x2;
    this.messages['result'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'result';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['command_id', amqp_types['sequence_no'], true, 1]);

        // None
        this.fields.push(['value', amqp_types['struct32'], false, 2]);




    });
    this.message_codes[0x2] = this.messages['result'];

    // notifies a peer of an execution error
    this.messages['EXCEPTION'] = 0x3;
    this.messages['exception'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'exception';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // error code indicating the         type of error
        this.fields.push(['error_code', amqp_types['uint16'], true, 1]);

        // exceptional command
        this.fields.push(['command_id', amqp_types['sequence_no'], false, 2]);

        // the class code of the command whose execution         gave rise to the error (if appropriate)
        this.fields.push(['class_code', amqp_types['uint8'], false, 4]);

        // the class code of the command whose execution         gave rise to the error (if appropriate)
        this.fields.push(['command_code', amqp_types['uint8'], false, 8]);

        // index of the exceptional field
        this.fields.push(['field_index', amqp_types['uint8'], false, 16]);

        // descriptive text on the exception
        this.fields.push(['description', amqp_types['str16'], false, 32]);

        // map to carry additional information about the         error
        this.fields.push(['error_info', amqp_types['map'], false, 64]);




    });
    this.message_codes[0x3] = this.messages['exception'];


}();

amqp_classes['Execution'] = new function(){

    this.sync = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['execution'].messages['sync'](),
                                          parsed_data: params});
    }

    this.result = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['execution'].messages['result'](),
                                          parsed_data: params});
    }

    this.exception = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['execution'].messages['exception'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x3] = amqp_classes['execution'];

// message transfer
amqp_classes['MESSAGE'] = 0x4;
amqp_classes['message'] = new function(){
    var this_class = this;
    this.code = 0x4;
    this.name = 'message';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['DELIVERY_PROPERTIES'] = 0x1;
    this.structs['delivery_properties'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'delivery_properties';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // controls discard of unroutable messages
        this.fields.push(['discard_unroutable', amqp_types['bit'], false, 1]);

        // Consider message unroutable if it cannot be         processed immediately
        this.fields.push(['immediate', amqp_types['bit'], false, 2]);

        // redelivery flag
        this.fields.push(['redelivered', amqp_types['bit'], false, 4]);

        // message priority, 0 to 9
        this.fields.push(['priority', amqp_types['uint8'], true, 8]);

        // message persistence requirement
        this.fields.push(['delivery_mode', amqp_types['uint8'], true, 16]);

        // time to live in ms
        this.fields.push(['ttl', amqp_types['uint64'], false, 32]);

        // message timestamp
        this.fields.push(['timestamp', amqp_types['datetime'], false, 64]);

        // message expiration time
        this.fields.push(['expiration', amqp_types['datetime'], false, 128]);

        // originating exchange
        this.fields.push(['exchange', amqp_types['str8'], false, 256]);

        // message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 512]);

        // global id for message transfer
        this.fields.push(['resume_id', amqp_types['str16'], false, 1024]);

        // ttl in ms for interrupted message data
        this.fields.push(['resume_ttl', amqp_types['uint64'], false, 2048]);

    ;
    });
    this.struct_codes[0x1] = this.structs['delivery_properties'];

    this.structs['FRAGMENT_PROPERTIES'] = 0x2;
    this.structs['fragment_properties'] = Class(StructMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'fragment_properties';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['first', amqp_types['bit'], false, 1]);

        // None
        this.fields.push(['last', amqp_types['bit'], false, 2]);

        // None
        this.fields.push(['fragment_size', amqp_types['uint64'], false, 4]);

    ;
    });
    this.struct_codes[0x2] = this.structs['fragment_properties'];

    this.structs['REPLY_TO'] = 0;
    this.structs['reply_to'] = Class(StructMarshaler, function(s) {
        this.code = 0;
        this.name = 'reply_to';
        this.pack_size = 2;
        this.size = 2;
        this.parent_class = this_class;
        this.fields = [];

        // the name of the exchange to reply to
        this.fields.push(['exchange', amqp_types['str8'], false, 1]);

        // the routing-key to use when replying
        this.fields.push(['routing_key', amqp_types['str8'], false, 2]);

    ;
    });
    this.struct_codes[0] = this.structs['reply_to'];

    this.structs['MESSAGE_PROPERTIES'] = 0x3;
    this.structs['message_properties'] = Class(StructMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'message_properties';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // length of the body segment in bytes
        this.fields.push(['content_length', amqp_types['uint64'], false, 1]);

        // application message identifier
        this.fields.push(['message_id', amqp_types['uuid'], false, 2]);

        // application correlation identifier
        this.fields.push(['correlation_id', amqp_types['vbin16'], false, 4]);

        // destination to reply to
        this.fields.push(['reply_to', this.parent_class.structs['reply_to'], false, 8]);

        // MIME content type
        this.fields.push(['content_type', amqp_types['str8'], false, 16]);

        // MIME content encoding
        this.fields.push(['content_encoding', amqp_types['str8'], false, 32]);

        // creating user id
        this.fields.push(['user_id', amqp_types['vbin16'], false, 64]);

        // creating application id
        this.fields.push(['app_id', amqp_types['vbin16'], false, 128]);

        // application specific headers table
        this.fields.push(['application_headers', amqp_types['map'], false, 256]);

    ;
    });
    this.struct_codes[0x3] = this.structs['message_properties'];

    this.structs['ACQUIRED'] = 0x4;
    this.structs['acquired'] = Class(StructMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'acquired';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['transfers', amqp_types['sequence_set'], true, 1]);

    ;
    });
    this.struct_codes[0x4] = this.structs['acquired'];

    this.structs['MESSAGE_RESUME_RESULT'] = 0x5;
    this.structs['message_resume_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'message_resume_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['offset', amqp_types['uint64'], false, 1]);

    ;
    });
    this.struct_codes[0x5] = this.structs['message_resume_result'];



    // transfer a message
    this.messages['TRANSFER'] = 0x1;
    this.messages['transfer'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'transfer';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // message destination
        this.fields.push(['destination', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['accept_mode', amqp_types['uint8'], true, 2]);

        // None
        this.fields.push(['acquire_mode', amqp_types['uint8'], true, 4]);



        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['delivery_properties','fragment_properties','message_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0x1] = this.messages['transfer'];

    // reject a message
    this.messages['ACCEPT'] = 0x2;
    this.messages['accept'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'accept';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['transfers', amqp_types['sequence_set'], true, 1]);




    });
    this.message_codes[0x2] = this.messages['accept'];

    // reject a message
    this.messages['REJECT'] = 0x3;
    this.messages['reject'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'reject';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['transfers', amqp_types['sequence_set'], true, 1]);

        // None
        this.fields.push(['code', amqp_types['uint16'], true, 2]);

        // informational text for message reject
        this.fields.push(['text', amqp_types['str8'], false, 4]);




    });
    this.message_codes[0x3] = this.messages['reject'];

    // release a message
    this.messages['RELEASE'] = 0x4;
    this.messages['release'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'release';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['transfers', amqp_types['sequence_set'], true, 1]);

        // mark the released messages as redelivered
        this.fields.push(['set_redelivered', amqp_types['bit'], false, 2]);




    });
    this.message_codes[0x4] = this.messages['release'];

    // acquire messages for consumption
    this.messages['ACQUIRE'] = 0x5;
    this.messages['acquire'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'acquire';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['transfers', amqp_types['sequence_set'], true, 1]);




    });
    this.message_codes[0x5] = this.messages['acquire'];

    // resume an interrupted message transfer
    this.messages['RESUME'] = 0x6;
    this.messages['resume'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'resume';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['resume_id', amqp_types['str16'], true, 2]);




    });
    this.message_codes[0x6] = this.messages['resume'];

    // start a queue subscription
    this.messages['SUBSCRIBE'] = 0x7;
    this.messages['subscribe'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'subscribe';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // incoming message destination
        this.fields.push(['destination', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['accept_mode', amqp_types['uint8'], true, 4]);

        // None
        this.fields.push(['acquire_mode', amqp_types['uint8'], true, 8]);

        // request exclusive access
        this.fields.push(['exclusive', amqp_types['bit'], false, 16]);

        // None
        this.fields.push(['resume_id', amqp_types['str16'], false, 32]);

        // None
        this.fields.push(['resume_ttl', amqp_types['uint64'], false, 64]);

        // arguments for vendor extensions
        this.fields.push(['arguments', amqp_types['map'], false, 128]);




    });
    this.message_codes[0x7] = this.messages['subscribe'];

    // end a queue subscription
    this.messages['CANCEL'] = 0x8;
    this.messages['cancel'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'cancel';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], true, 1]);




    });
    this.message_codes[0x8] = this.messages['cancel'];

    // set the flow control mode
    this.messages['SET_FLOW_MODE'] = 0x9;
    this.messages['set_flow_mode'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x9;
        this.name = 'set_flow_mode';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['flow_mode', amqp_types['uint8'], true, 2]);




    });
    this.message_codes[0x9] = this.messages['set_flow_mode'];

    // control message flow
    this.messages['FLOW'] = 0xa;
    this.messages['flow'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xa;
        this.name = 'flow';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['unit', amqp_types['uint8'], true, 2]);

        // None
        this.fields.push(['value', amqp_types['uint32'], false, 4]);




    });
    this.message_codes[0xa] = this.messages['flow'];

    // force the sending of available messages
    this.messages['FLUSH'] = 0xb;
    this.messages['flush'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xb;
        this.name = 'flush';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0xb] = this.messages['flush'];

    // stop the sending of messages
    this.messages['STOP'] = 0xc;
    this.messages['stop'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xc;
        this.name = 'stop';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['destination', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0xc] = this.messages['stop'];


}();

amqp_classes['Message'] = new function(){

    this.transfer = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['transfer'](),
                                          parsed_data: params});
    }

    this.accept = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['accept'](),
                                          parsed_data: params});
    }

    this.reject = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['reject'](),
                                          parsed_data: params});
    }

    this.release = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['release'](),
                                          parsed_data: params});
    }

    this.acquire = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['acquire'](),
                                          parsed_data: params});
    }

    this.resume = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['resume'](),
                                          parsed_data: params});
    }

    this.subscribe = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['subscribe'](),
                                          parsed_data: params});
    }

    this.cancel = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['cancel'](),
                                          parsed_data: params});
    }

    this.set_flow_mode = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['set_flow_mode'](),
                                          parsed_data: params});
    }

    this.flow = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['flow'](),
                                          parsed_data: params});
    }

    this.flush = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['flush'](),
                                          parsed_data: params});
    }

    this.stop = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['message'].messages['stop'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x4] = amqp_classes['message'];

// work with standard transactions
amqp_classes['TX'] = 0x5;
amqp_classes['tx'] = new function(){
    var this_class = this;
    this.code = 0x5;
    this.name = 'tx';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};



    // select standard transaction mode
    this.messages['SELECT'] = 0x1;
    this.messages['select'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'select';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x1] = this.messages['select'];

    // commit the current transaction
    this.messages['COMMIT'] = 0x2;
    this.messages['commit'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'commit';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x2] = this.messages['commit'];

    // abandon the current transaction
    this.messages['ROLLBACK'] = 0x3;
    this.messages['rollback'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'rollback';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x3] = this.messages['rollback'];


}();

amqp_classes['Tx'] = new function(){

    this.select = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['tx'].messages['select'](),
                                          parsed_data: params});
    }

    this.commit = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['tx'].messages['commit'](),
                                          parsed_data: params});
    }

    this.rollback = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['tx'].messages['rollback'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x5] = amqp_classes['tx'];

// Demarcates dtx branches
amqp_classes['DTX'] = 0x6;
amqp_classes['dtx'] = new function(){
    var this_class = this;
    this.code = 0x6;
    this.name = 'dtx';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['XA_RESULT'] = 0x1;
    this.structs['xa_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'xa_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['status', amqp_types['uint16'], true, 1]);

    ;
    });
    this.struct_codes[0x1] = this.structs['xa_result'];

    this.structs['XID'] = 0x4;
    this.structs['xid'] = Class(StructMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'xid';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // implementation specific format code
        this.fields.push(['format', amqp_types['uint32'], true, 1]);

        // global transaction id
        this.fields.push(['global_id', amqp_types['vbin8'], true, 2]);

        // branch qualifier
        this.fields.push(['branch_id', amqp_types['vbin8'], true, 4]);

    ;
    });
    this.struct_codes[0x4] = this.structs['xid'];

    this.structs['GET_TIMEOUT_RESULT'] = 0x2;
    this.structs['get_timeout_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'get_timeout_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // The current transaction timeout value
        this.fields.push(['timeout', amqp_types['uint32'], true, 1]);

    ;
    });
    this.struct_codes[0x2] = this.structs['get_timeout_result'];

    this.structs['RECOVER_RESULT'] = 0x3;
    this.structs['recover_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'recover_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // array of xids to be recovered
        this.fields.push(['in_doubt', amqp_types['array'], true, 1]);

    ;
    });
    this.struct_codes[0x3] = this.structs['recover_result'];



    // Select dtx mode
    this.messages['SELECT'] = 0x1;
    this.messages['select'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'select';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x1] = this.messages['select'];

    // Start a dtx branch
    this.messages['START'] = 0x2;
    this.messages['start'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'start';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);

        // Join with existing xid flag
        this.fields.push(['join', amqp_types['bit'], false, 2]);

        // Resume flag
        this.fields.push(['resume', amqp_types['bit'], false, 4]);




    });
    this.message_codes[0x2] = this.messages['start'];

    // End a dtx branch
    this.messages['END'] = 0x3;
    this.messages['end'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'end';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);

        // Failure flag
        this.fields.push(['fail', amqp_types['bit'], false, 2]);

        // Temporary suspension flag
        this.fields.push(['suspend', amqp_types['bit'], false, 4]);




    });
    this.message_codes[0x3] = this.messages['end'];

    // Commit work on dtx branch
    this.messages['COMMIT'] = 0x4;
    this.messages['commit'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'commit';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);

        // One-phase optimization flag
        this.fields.push(['one_phase', amqp_types['bit'], false, 2]);




    });
    this.message_codes[0x4] = this.messages['commit'];

    // Discard dtx branch
    this.messages['FORGET'] = 0x5;
    this.messages['forget'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'forget';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);




    });
    this.message_codes[0x5] = this.messages['forget'];

    // Obtain dtx timeout in seconds
    this.messages['GET_TIMEOUT'] = 0x6;
    this.messages['get_timeout'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'get_timeout';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);




    });
    this.message_codes[0x6] = this.messages['get_timeout'];

    // Prepare a dtx branch
    this.messages['PREPARE'] = 0x7;
    this.messages['prepare'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'prepare';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);




    });
    this.message_codes[0x7] = this.messages['prepare'];

    // Get prepared or completed xids
    this.messages['RECOVER'] = 0x8;
    this.messages['recover'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'recover';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x8] = this.messages['recover'];

    // Rollback a dtx branch
    this.messages['ROLLBACK'] = 0x9;
    this.messages['rollback'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x9;
        this.name = 'rollback';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);




    });
    this.message_codes[0x9] = this.messages['rollback'];

    // Set dtx timeout value
    this.messages['SET_TIMEOUT'] = 0xa;
    this.messages['set_timeout'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xa;
        this.name = 'set_timeout';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // Transaction xid
        this.fields.push(['xid', this.parent_class.structs['xid'], true, 1]);

        // Dtx timeout in seconds
        this.fields.push(['timeout', amqp_types['uint32'], true, 2]);




    });
    this.message_codes[0xa] = this.messages['set_timeout'];


}();

amqp_classes['Dtx'] = new function(){

    this.select = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['select'](),
                                          parsed_data: params});
    }

    this.start = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['start'](),
                                          parsed_data: params});
    }

    this.end = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['end'](),
                                          parsed_data: params});
    }

    this.commit = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['commit'](),
                                          parsed_data: params});
    }

    this.forget = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['forget'](),
                                          parsed_data: params});
    }

    this.get_timeout = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['get_timeout'](),
                                          parsed_data: params});
    }

    this.prepare = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['prepare'](),
                                          parsed_data: params});
    }

    this.recover = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['recover'](),
                                          parsed_data: params});
    }

    this.rollback = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['rollback'](),
                                          parsed_data: params});
    }

    this.set_timeout = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['dtx'].messages['set_timeout'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x6] = amqp_classes['dtx'];

// work with exchanges
amqp_classes['EXCHANGE'] = 0x7;
amqp_classes['exchange'] = new function(){
    var this_class = this;
    this.code = 0x7;
    this.name = 'exchange';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['EXCHANGE_QUERY_RESULT'] = 0x1;
    this.structs['exchange_query_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'exchange_query_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // indicate the exchange type
        this.fields.push(['type', amqp_types['str8'], false, 1]);

        // indicate the durability
        this.fields.push(['durable', amqp_types['bit'], false, 2]);

        // indicate an unknown exchange
        this.fields.push(['not_found', amqp_types['bit'], false, 4]);

        // other unspecified exchange properties
        this.fields.push(['arguments', amqp_types['map'], false, 8]);

    ;
    });
    this.struct_codes[0x1] = this.structs['exchange_query_result'];

    this.structs['EXCHANGE_BOUND_RESULT'] = 0x2;
    this.structs['exchange_bound_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'exchange_bound_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // indicate an unknown exchange
        this.fields.push(['exchange_not_found', amqp_types['bit'], false, 1]);

        // indicate an unknown queue
        this.fields.push(['queue_not_found', amqp_types['bit'], false, 2]);

        // indicate no matching queue
        this.fields.push(['queue_not_matched', amqp_types['bit'], false, 4]);

        // indicate no matching binding-key
        this.fields.push(['key_not_matched', amqp_types['bit'], false, 8]);

        // indicate no matching arguments
        this.fields.push(['args_not_matched', amqp_types['bit'], false, 16]);

    ;
    });
    this.struct_codes[0x2] = this.structs['exchange_bound_result'];



    // verify exchange exists, create if needed
    this.messages['DECLARE'] = 0x1;
    this.messages['declare'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'declare';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['exchange', amqp_types['str8'], true, 1]);

        // exchange type
        this.fields.push(['type', amqp_types['str8'], true, 2]);

        // exchange name for unroutable messages
        this.fields.push(['alternate_exchange', amqp_types['str8'], false, 4]);

        // do not create exchange
        this.fields.push(['passive', amqp_types['bit'], false, 8]);

        // request a durable exchange
        this.fields.push(['durable', amqp_types['bit'], false, 16]);

        // auto-delete when unused
        this.fields.push(['auto_delete', amqp_types['bit'], false, 32]);

        // arguments for declaration
        this.fields.push(['arguments', amqp_types['map'], false, 64]);




    });
    this.message_codes[0x1] = this.messages['declare'];

    // delete an exchange
    this.messages['DELETE'] = 0x2;
    this.messages['delete'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'delete';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['exchange', amqp_types['str8'], true, 1]);

        // delete only if unused
        this.fields.push(['if_unused', amqp_types['bit'], false, 2]);




    });
    this.message_codes[0x2] = this.messages['delete'];

    // request information about an exchange
    this.messages['QUERY'] = 0x3;
    this.messages['query'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'query';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // the exchange name
        this.fields.push(['name', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0x3] = this.messages['query'];

    // bind queue to an exchange
    this.messages['BIND'] = 0x4;
    this.messages['bind'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'bind';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // name of the exchange to bind to
        this.fields.push(['exchange', amqp_types['str8'], true, 2]);

        // identifies a binding between a given exchange and queue
        this.fields.push(['binding_key', amqp_types['str8'], true, 4]);

        // arguments for binding
        this.fields.push(['arguments', amqp_types['map'], false, 8]);




    });
    this.message_codes[0x4] = this.messages['bind'];

    // unbind a queue from an exchange
    this.messages['UNBIND'] = 0x5;
    this.messages['unbind'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'unbind';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // None
        this.fields.push(['exchange', amqp_types['str8'], true, 2]);

        // the key of the binding
        this.fields.push(['binding_key', amqp_types['str8'], true, 4]);




    });
    this.message_codes[0x5] = this.messages['unbind'];

    // request information about bindings to an exchange
    this.messages['BOUND'] = 0x6;
    this.messages['bound'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'bound';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // the exchange name
        this.fields.push(['exchange', amqp_types['str8'], false, 1]);

        // a queue name
        this.fields.push(['queue', amqp_types['str8'], true, 2]);

        // a binding-key
        this.fields.push(['binding_key', amqp_types['str8'], false, 4]);

        // a set of binding arguments
        this.fields.push(['arguments', amqp_types['map'], false, 8]);




    });
    this.message_codes[0x6] = this.messages['bound'];


}();

amqp_classes['Exchange'] = new function(){

    this.declare = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['declare'](),
                                          parsed_data: params});
    }

    this.delete = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['delete'](),
                                          parsed_data: params});
    }

    this.query = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['query'](),
                                          parsed_data: params});
    }

    this.bind = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['bind'](),
                                          parsed_data: params});
    }

    this.unbind = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['unbind'](),
                                          parsed_data: params});
    }

    this.bound = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['exchange'].messages['bound'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x7] = amqp_classes['exchange'];

// work with queues
amqp_classes['QUEUE'] = 0x8;
amqp_classes['queue'] = new function(){
    var this_class = this;
    this.code = 0x8;
    this.name = 'queue';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['QUEUE_QUERY_RESULT'] = 0x1;
    this.structs['queue_query_result'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'queue_query_result';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // None
        this.fields.push(['alternate_exchange', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['durable', amqp_types['bit'], false, 4]);

        // None
        this.fields.push(['exclusive', amqp_types['bit'], false, 8]);

        // None
        this.fields.push(['auto_delete', amqp_types['bit'], false, 16]);

        // None
        this.fields.push(['arguments', amqp_types['map'], false, 32]);

        // number of messages in queue
        this.fields.push(['message_count', amqp_types['uint32'], true, 64]);

        // number of subscribers
        this.fields.push(['subscriber_count', amqp_types['uint32'], true, 128]);

    ;
    });
    this.struct_codes[0x1] = this.structs['queue_query_result'];



    // declare queue
    this.messages['DECLARE'] = 0x1;
    this.messages['declare'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'declare';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // exchange name for messages with exceptions
        this.fields.push(['alternate_exchange', amqp_types['str8'], false, 2]);

        // do not create queue
        this.fields.push(['passive', amqp_types['bit'], false, 4]);

        // request a durable queue
        this.fields.push(['durable', amqp_types['bit'], false, 8]);

        // request an exclusive queue
        this.fields.push(['exclusive', amqp_types['bit'], false, 16]);

        // auto-delete queue when unused
        this.fields.push(['auto_delete', amqp_types['bit'], false, 32]);

        // arguments for declaration
        this.fields.push(['arguments', amqp_types['map'], false, 64]);




    });
    this.message_codes[0x1] = this.messages['declare'];

    // delete a queue
    this.messages['DELETE'] = 0x2;
    this.messages['delete'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'delete';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);

        // delete only if unused
        this.fields.push(['if_unused', amqp_types['bit'], false, 2]);

        // delete only if empty
        this.fields.push(['if_empty', amqp_types['bit'], false, 4]);




    });
    this.message_codes[0x2] = this.messages['delete'];

    // purge a queue
    this.messages['PURGE'] = 0x3;
    this.messages['purge'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'purge';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], true, 1]);




    });
    this.message_codes[0x3] = this.messages['purge'];

    // request information about a queue
    this.messages['QUERY'] = 0x4;
    this.messages['query'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'query';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // the queried queue
        this.fields.push(['queue', amqp_types['str8'], true, 1]);




    });
    this.message_codes[0x4] = this.messages['query'];


}();

amqp_classes['Queue'] = new function(){

    this.declare = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['queue'].messages['declare'](),
                                          parsed_data: params});
    }

    this.delete = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['queue'].messages['delete'](),
                                          parsed_data: params});
    }

    this.purge = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['queue'].messages['purge'](),
                                          parsed_data: params});
    }

    this.query = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['queue'].messages['query'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x8] = amqp_classes['queue'];

// work with file content
amqp_classes['FILE'] = 0x9;
amqp_classes['file'] = new function(){
    var this_class = this;
    this.code = 0x9;
    this.name = 'file';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['FILE_PROPERTIES'] = 0x1;
    this.structs['file_properties'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'file_properties';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // MIME content type
        this.fields.push(['content_type', amqp_types['str8'], false, 1]);

        // MIME content encoding
        this.fields.push(['content_encoding', amqp_types['str8'], false, 2]);

        // message header field table
        this.fields.push(['headers', amqp_types['map'], false, 4]);

        // message priority, 0 to 9
        this.fields.push(['priority', amqp_types['uint8'], false, 8]);

        // destination to reply to
        this.fields.push(['reply_to', amqp_types['str8'], false, 16]);

        // application message identifier
        this.fields.push(['message_id', amqp_types['str8'], false, 32]);

        // message filename
        this.fields.push(['filename', amqp_types['str8'], false, 64]);

        // message timestamp
        this.fields.push(['timestamp', amqp_types['datetime'], false, 128]);

        // intra-cluster routing identifier
        this.fields.push(['cluster_id', amqp_types['str8'], false, 256]);

    ;
    });
    this.struct_codes[0x1] = this.structs['file_properties'];



    // specify quality of service
    this.messages['QOS'] = 0x1;
    this.messages['qos'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'qos';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // pre-fetch window in octets
        this.fields.push(['prefetch_size', amqp_types['uint32'], false, 1]);

        // pre-fetch window in messages
        this.fields.push(['prefetch_count', amqp_types['uint16'], false, 2]);

        // apply to entire connection
        this.fields.push(['global', amqp_types['bit'], false, 4]);




    });
    this.message_codes[0x1] = this.messages['qos'];

    // confirm the requested qos
    this.messages['QOS_OK'] = 0x2;
    this.messages['qos_ok'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'qos_ok';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x2] = this.messages['qos_ok'];

    // start a queue consumer
    this.messages['CONSUME'] = 0x3;
    this.messages['consume'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'consume';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['no_local', amqp_types['bit'], false, 4]);

        // no acknowledgement needed
        this.fields.push(['no_ack', amqp_types['bit'], false, 8]);

        // request exclusive access
        this.fields.push(['exclusive', amqp_types['bit'], false, 16]);

        // do not send a reply command
        this.fields.push(['nowait', amqp_types['bit'], false, 32]);

        // arguments for consuming
        this.fields.push(['arguments', amqp_types['map'], false, 64]);




    });
    this.message_codes[0x3] = this.messages['consume'];

    // confirm a new consumer
    this.messages['CONSUME_OK'] = 0x4;
    this.messages['consume_ok'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'consume_ok';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0x4] = this.messages['consume_ok'];

    // end a queue consumer
    this.messages['CANCEL'] = 0x5;
    this.messages['cancel'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'cancel';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0x5] = this.messages['cancel'];

    // request to start staging
    this.messages['OPEN'] = 0x6;
    this.messages['open'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'open';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // staging identifier
        this.fields.push(['identifier', amqp_types['str8'], false, 1]);

        // message content size
        this.fields.push(['content_size', amqp_types['uint64'], false, 2]);




    });
    this.message_codes[0x6] = this.messages['open'];

    // confirm staging ready
    this.messages['OPEN_OK'] = 0x7;
    this.messages['open_ok'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'open_ok';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // already staged amount
        this.fields.push(['staged_size', amqp_types['uint64'], false, 1]);




    });
    this.message_codes[0x7] = this.messages['open_ok'];

    // stage message content
    this.messages['STAGE'] = 0x8;
    this.messages['stage'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'stage';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];




        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['file_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0x8] = this.messages['stage'];

    // publish a message
    this.messages['PUBLISH'] = 0x9;
    this.messages['publish'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x9;
        this.name = 'publish';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 1]);

        // Message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 2]);

        // indicate mandatory routing
        this.fields.push(['mandatory', amqp_types['bit'], false, 4]);

        // request immediate delivery
        this.fields.push(['immediate', amqp_types['bit'], false, 8]);

        // staging identifier
        this.fields.push(['identifier', amqp_types['str8'], false, 16]);




    });
    this.message_codes[0x9] = this.messages['publish'];

    // return a failed message
    this.messages['RETURN'] = 0xa;
    this.messages['return'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xa;
        this.name = 'return';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['reply_code', amqp_types['uint16'], false, 1]);

        // The localized reply text.
        this.fields.push(['reply_text', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 4]);

        // Message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 8]);



        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['file_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0xa] = this.messages['return'];

    // notify the client of a consumer message
    this.messages['DELIVER'] = 0xb;
    this.messages['deliver'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xb;
        this.name = 'deliver';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['delivery_tag', amqp_types['uint64'], false, 2]);

        // Indicate possible duplicate delivery
        this.fields.push(['redelivered', amqp_types['bit'], false, 4]);

        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 8]);

        // Message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 16]);

        // staging identifier
        this.fields.push(['identifier', amqp_types['str8'], false, 32]);




    });
    this.message_codes[0xb] = this.messages['deliver'];

    // acknowledge one or more messages
    this.messages['ACK'] = 0xc;
    this.messages['ack'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xc;
        this.name = 'ack';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['delivery_tag', amqp_types['uint64'], false, 1]);

        // acknowledge multiple messages
        this.fields.push(['multiple', amqp_types['bit'], false, 2]);




    });
    this.message_codes[0xc] = this.messages['ack'];

    // reject an incoming message
    this.messages['REJECT'] = 0xd;
    this.messages['reject'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0xd;
        this.name = 'reject';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['delivery_tag', amqp_types['uint64'], false, 1]);

        // requeue the message
        this.fields.push(['requeue', amqp_types['bit'], false, 2]);




    });
    this.message_codes[0xd] = this.messages['reject'];


}();

amqp_classes['File'] = new function(){

    this.qos = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['qos'](),
                                          parsed_data: params});
    }

    this.qos_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['qos_ok'](),
                                          parsed_data: params});
    }

    this.consume = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['consume'](),
                                          parsed_data: params});
    }

    this.consume_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['consume_ok'](),
                                          parsed_data: params});
    }

    this.cancel = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['cancel'](),
                                          parsed_data: params});
    }

    this.open = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['open'](),
                                          parsed_data: params});
    }

    this.open_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['open_ok'](),
                                          parsed_data: params});
    }

    this.stage = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['stage'](),
                                          parsed_data: params});
    }

    this.publish = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['publish'](),
                                          parsed_data: params});
    }

    this.return = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['return'](),
                                          parsed_data: params});
    }

    this.deliver = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['deliver'](),
                                          parsed_data: params});
    }

    this.ack = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['ack'](),
                                          parsed_data: params});
    }

    this.reject = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['file'].messages['reject'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0x9] = amqp_classes['file'];

// work with streaming content
amqp_classes['STREAM'] = 0xa;
amqp_classes['stream'] = new function(){
    var this_class = this;
    this.code = 0xa;
    this.name = 'stream';
    this.structs = {};
    this.struct_codes = {};
    this.messages = {};
    this.message_codes = {};

    this.structs['STREAM_PROPERTIES'] = 0x1;
    this.structs['stream_properties'] = Class(StructMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'stream_properties';
        this.pack_size = 2;
        this.size = 4;
        this.parent_class = this_class;
        this.fields = [];

        // MIME content type
        this.fields.push(['content_type', amqp_types['str8'], false, 1]);

        // MIME content encoding
        this.fields.push(['content_encoding', amqp_types['str8'], false, 2]);

        // message header field table
        this.fields.push(['headers', amqp_types['map'], false, 4]);

        // message priority, 0 to 9
        this.fields.push(['priority', amqp_types['uint8'], false, 8]);

        // message timestamp
        this.fields.push(['timestamp', amqp_types['datetime'], false, 16]);

    ;
    });
    this.struct_codes[0x1] = this.structs['stream_properties'];



    // specify quality of service
    this.messages['QOS'] = 0x1;
    this.messages['qos'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x1;
        this.name = 'qos';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // pre-fetch window in octets
        this.fields.push(['prefetch_size', amqp_types['uint32'], false, 1]);

        // pre-fetch window in messages
        this.fields.push(['prefetch_count', amqp_types['uint16'], false, 2]);

        // transfer rate in octets/second
        this.fields.push(['consume_rate', amqp_types['uint32'], false, 4]);

        // apply to entire connection
        this.fields.push(['global', amqp_types['bit'], false, 8]);




    });
    this.message_codes[0x1] = this.messages['qos'];

    // confirm the requested qos
    this.messages['QOS_OK'] = 0x2;
    this.messages['qos_ok'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x2;
        this.name = 'qos_ok';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];





    });
    this.message_codes[0x2] = this.messages['qos_ok'];

    // start a queue consumer
    this.messages['CONSUME'] = 0x3;
    this.messages['consume'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x3;
        this.name = 'consume';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['queue', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['no_local', amqp_types['bit'], false, 4]);

        // request exclusive access
        this.fields.push(['exclusive', amqp_types['bit'], false, 8]);

        // do not send a reply command
        this.fields.push(['nowait', amqp_types['bit'], false, 16]);

        // arguments for consuming
        this.fields.push(['arguments', amqp_types['map'], false, 32]);




    });
    this.message_codes[0x3] = this.messages['consume'];

    // confirm a new consumer
    this.messages['CONSUME_OK'] = 0x4;
    this.messages['consume_ok'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x4;
        this.name = 'consume_ok';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0x4] = this.messages['consume_ok'];

    // end a queue consumer
    this.messages['CANCEL'] = 0x5;
    this.messages['cancel'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x5;
        this.name = 'cancel';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);




    });
    this.message_codes[0x5] = this.messages['cancel'];

    // publish a message
    this.messages['PUBLISH'] = 0x6;
    this.messages['publish'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x6;
        this.name = 'publish';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 1]);

        // Message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 2]);

        // indicate mandatory routing
        this.fields.push(['mandatory', amqp_types['bit'], false, 4]);

        // request immediate delivery
        this.fields.push(['immediate', amqp_types['bit'], false, 8]);



        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['stream_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0x6] = this.messages['publish'];

    // return a failed message
    this.messages['RETURN'] = 0x7;
    this.messages['return'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x7;
        this.name = 'return';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['reply_code', amqp_types['uint16'], false, 1]);

        // The localized reply text.
        this.fields.push(['reply_text', amqp_types['str8'], false, 2]);

        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 4]);

        // Message routing key
        this.fields.push(['routing_key', amqp_types['str8'], false, 8]);



        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['stream_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0x7] = this.messages['return'];

    // notify the client of a consumer message
    this.messages['DELIVER'] = 0x8;
    this.messages['deliver'] = Class(CommandMessageMarshaler, function(s) {
        this.code = 0x8;
        this.name = 'deliver';
        this.parent_class = this_class;
        this.fields = [];
        this.segments = [];


        // None
        this.fields.push(['consumer_tag', amqp_types['str8'], false, 1]);

        // None
        this.fields.push(['delivery_tag', amqp_types['uint64'], false, 2]);

        // None
        this.fields.push(['exchange', amqp_types['str8'], false, 4]);

        // None
        this.fields.push(['queue', amqp_types['str8'], true, 8]);



        this.segments.push({
            name: '_header',
            marshaler: Class(HeaderSegmentMarshaler, function(s) {
                this.parent_class = this_class;
                this.entries = ['stream_properties'];
            })
        });

        this.segments.push({
            name: '_body',
            marshaler: BodySegmentMarshaler
        });


    });
    this.message_codes[0x8] = this.messages['deliver'];


}();

amqp_classes['Stream'] = new function(){

    this.qos = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['qos'](),
                                          parsed_data: params});
    }

    this.qos_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['qos_ok'](),
                                          parsed_data: params});
    }

    this.consume = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['consume'](),
                                          parsed_data: params});
    }

    this.consume_ok = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['consume_ok'](),
                                          parsed_data: params});
    }

    this.cancel = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['cancel'](),
                                          parsed_data: params});
    }

    this.publish = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['publish'](),
                                          parsed_data: params});
    }

    this.return = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['return'](),
                                          parsed_data: params});
    }

    this.deliver = function(params) {
        return new amqp.protocol.Message({marshaler: new amqp_classes['stream'].messages['deliver'](),
                                          parsed_data: params});
    }


}();
amqp_classcodes[0xa] = amqp_classes['stream'];


exports.version = version;

exports.lookup_type = lookup_type;
exports.lookup_class = lookup_class;
exports.get_header = get_header;
exports.guess_type = guess_type;

exports.amqp_types = amqp_types;
exports.amqp_typecodes = amqp_typecodes;
exports.amqp_classes = amqp_classes;
exports.amqp_classcodes = amqp_classcodes;

exports.Frame = Frame;
exports.Connection = Connection;

})();
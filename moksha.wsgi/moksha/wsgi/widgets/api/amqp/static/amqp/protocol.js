(function(){

jsio("import Class");
jsio('import jsio.logging');

var logger = jsio.logging.getLogger('AmqpProtocol');

// noop console if it doesn't exist
if (typeof(console) == 'undefined') {
    console = {log:function() {return;}};
}

var deep_copy_defaults = function(o) {
    var results = null;
    if (o != null && typeof(o) == 'object') {
        if (o instanceof Array) {
            results = [];
            for(var i=0; i<o.length; i++)
                results.push(deep_copy_defaults(o[i]));
        } else {
            results = {}
            for(var prop in o) {
                results[prop] = deep_copy_defaults(o[prop]);
            }
        }
    } else {
        results = o;
    }

    return results;
};

var DefaultsClass = Class(function () {
    // create the class
    this.init = function(options, defaults) {
        if (typeof(defaults) == 'undefined' || defaults == null)
            return;

        for (var d in defaults) {
             if (d in options)
                this[d] = options[d];
             else
                this[d] = deep_copy_defaults(defaults[d]);
        }
    }
});

var extend = function(module, ext) {
    for (var key in ext) {
        module[key] = ext[key];
    }
};

var default_version = '0.10';
var protocols = {};

var register = function(module) {
    jsio("import " + module + " as amqp_module");
    var version = amqp_module.version.toString();
    if (protocols[version])
        throw "Version " + version + " of the AMQP bindings has already been registered.  Duplicate registration!!!";

    protocols[version] = amqp_module;

    var def_ver_check = default_version.split('.');
    var ver_check = version.split('.');

    for (var i=0; i < ver_check.length; i++) {
        if (ver_check[i] > def_ver_check[i]) {
            default_version = version;
            return;
        }
    }
};

var get_connection = function(version, options) {
    if (!version)
        version = default_version;

    var module = protocols[version];
    if (!module)
        throw ("Version " + version + " of the AMQP protocol was requested but has not yet been registered");

    return new module.Connection(options);
};

var AssemblyGroupReader = Class(function(supr) {
    this.init = function() {
        this._children = [];
        this._curr_child = null;
        this._curr_child_index = -1;
        this.metadata = {};

    };

    this.add_child = function(assembly) {
        if (this._curr_child == null) {
            this._curr_child = assembly;
            this._curr_child_index = 0;
        }

        this._children.push(assembly);
    };

    this.read_byte = function(count) {
        if (!this._curr_child)
            throw "Error trying to read from an assembly group with no children";

        var data = this._curr_child.read_byte(count);
        if (data.length < count) {
            var i = this._curr_child_index + 1;
            if (i >= this._children.length)
                return data;

            this._curr_child = this._children[i];
            this._curr_child_index = i;

            data += this.read_byte(count - data.length);
        }

        return data;
    };

    this.set_metadata = function(key, value) {
        this.metadata[key] = value;
    };

    this.get_metadata = function(key) {
        return this.metadata[key];
    };

    this.mark_start = function() {
        if (this._curr_child)
            this._curr_child.mark_start();
    };
});

var Assembly = Class(DefaultsClass, function(supr) {
    var defaults = {
        data: '',
        metadata:{}
    };

    this.init = function(options) {
        supr(this, 'init', [options, defaults]);
        // in bytes
        this._seek_pos = 0;
        this._bit_offset = 0;
        this._options = options;
        this._start_marker = 0;
    };

    this.read_bit = function(count) {
        var final_offset = this._bit_offset + count;
        if (final_offset > 8)
            throw RangeError("You tried to read beyond the byte boundry.  This is not allowed.  You may only read inside a single byte when reading individual bits");

        var c = this._options.data.charCodeAt(this._seek_pos);
        var mask = 1;
        for (var i = 1; i < count; i++)
            mask = (mask << 1) + 1;

        mask = mask << (7 - this._bit_offset);
        var c_offset = c & mask;
        var results = c_offset >> (8 - (count + this._bit_offset));

        if (final_offset == 8) {
            this._seek_pos++;
            this._bit_offset = 0;
        } else {
            this._bit_offset = final_offset;
        }

        return results;
    };

    this.read_byte = function(count) {
        if (this._bit_offset)
            throw RangeError("You tried to read a non-aligned byte.  This is not allowed.  This happens if you had previously called bit read and did not end your reads on a byte boundry!");

        var results = this.data.substr(this._seek_pos, count);
        this._seek_pos += count;

        return results;
    };

    this.write = function(bytes) {
        if (!this.data)
            this.data = bytes;
        else
            this.data += bytes;
    };

    this.prepend = function(bytes) {
        this.data = bytes + this.data;
    };

    this.get_data = function() {
        return this.data;
    };

    this.set_metadata = function(key, value) {
        this.metadata[key] = value;
    };

    this.get_metadata = function(key) {
        return this.metadata[key];
    };

    this.get_size = function(from_current_pos) {
        var length = this.data.length;
        if (from_current_pos)
            return length - this._seek_pos;
        else
            return length;
    };

    this.seek = function(pos) {
        this._seek_pos = pos;
        this._bit_offset = 0;
    };

    this.eof = function() {
        if (this.data.length == this._seek_pos)
            return true;
    };

    /* Debug metadata */
    this.mark_start = function() {
        this._start_marker = this._seek_pos;
    };

    this.get_start_pos = function() {
        return this._start_marker;
    };

    this.get_pos = function() {
        return this._seek_pos;
    };
});

var Message = Class(DefaultsClass, function (supr){
    var defaults = {
        parsed_data: {},
        marshaler: null
    };

    this.init = function(options) {
        supr(this, 'init', [options, defaults]);

        if (this.marshaler) {
            this.name = this.marshaler.name;
            this.parent_class = this.marshaler.parent_class;
            this.class_name = this.parent_class.name;
            this.code = this.marshaler.code;
            this.class_code = this.parent_class.code;
        }

        this._next_frame_index = 0;

        if (typeof(this.parsed_data) == 'undefined')
            this.parsed_data = {}

        this.assembly = new Assembly({});
        this._has_multiple_segments = false;
        this._frames = [];
    };

    this.get = function (key) {
        return this.parsed_data[key];
    };

    this.set = function (key, value) {
        this.parsed_data[key] = value;
        return value;
    };

    this.get_size = function() {
        return this.assembly.get_size(true);
    };

    this.get_data = function(size) {
        return this.assembly.read_byte(size);
    };

    this.get_type = function() {
        return this.marshaler.seg_type;
    };

    this.get_code = function() {
        return this.code;
    };

    this.get_class_code = function() {
        return this.class_code;
    };

    this.get_name = function() {
        return this.name;
    };

    this.get_class_name = function() {
        return this.class_name;
    };

    this.add_frame = function(frame) {
        this._frames.push(frame);
    };

    this.decode_next_segment = function() {
        if(this._next_frame_index == 0) {
            this.set('channel', this._frames[0].get('channel'));
            this.set('track', this._frames[0].get('track'));
        }

        this.assembly = new AssemblyGroupReader();
        var _payload_size = 0;
        var frame = null;

        do {
            frame = this._frames[this._next_frame_index];

            this.assembly.add_child(frame.assembly);
            _payload_size += frame.get('payload_size');
            this._next_frame_index++;
        } while(!frame.get('is_last_frame'));

        this._current_segment_type = frame.get('segment_type');

        this.assembly.set_metadata('payload_size', _payload_size);
    };

    this.encode = function() {
        this.marshaler.set_value(this.parsed_data);
        this.marshaler.encode(this.assembly);
        if (this.assembly.get_metadata('has_multiple_segments'))
            this._has_multiple_segments = true;
    };

    this.has_multiple_segments = function() {
        return this._has_multiple_segments;
    };

    this.get_segment_frames = function() {
        return this.assembly.get_metadata('segment_frames')
    };
});

// decoders and encoders
var int_to_bytestr = function(u, size) {
    var results = '';
    var u_shifted = u;
    var mask = 255;
    for (var i=0; i < size; i++) {
        // shift and mask bits in network order
        var u_mask = u_shifted & mask;
        results = String.fromCharCode(u_mask) + results;

        u_shifted = u_shifted >> 8;
    }

    return results;
};

var decode_typecode = function(assembly) {
    return decode_uint(assembly, 1);
};

var encode_typecode = function(assembly, typecode) {
    if (typecode != null) {
        var b = int_to_bytestr(typecode, 1);
        assembly.write(b);
    }
};

var decode_bin = function(assembly, size) {
    return (assembly.read_byte(size));
};

var encode_bin = function(assembly, typecode, size, value) {
    encode_typecode(assembly, typecode);
    assembly.write(value)
};

var decode_int = function(assembly, size) {
    var stream = assembly.read_byte(size);
    var first_byte = stream.charCodeAt(0);
    var sign_mask = 128;
    var num_mask = 127;
    var sign = first_byte & sign_mask;
    first_byte = first_byte & num_mask;
    if(sign)
        first_byte = ~first_byte

    first_byte = first_byte << ((size - 1) * 8);

    var result = first_byte;
    for (var i = 0; i < size-1; i++) {
        var byte_pos = size - (i + 1);
        var byte = stream.charCodeAt(byte_pos);
        if (sign)
            byte = ~byte;
        result += byte << (i * 8);
    }

    if (sign)
        result = (result + 1) * -1;

    return result;

};

var encode_int = function(assembly, typecode, size, value) {
    encode_typecode(assembly, typecode);
    var byte_value = int_to_bytestr(value, size);
    assembly.write(byte_value);
};

var decode_uint = function(assembly, size) {
    var stream = assembly.read_byte(size);

    var result = 0;
    for (var i = 0; i < size; i++) {
        var byte_pos = size - (i + 1);
        result += stream.charCodeAt(byte_pos) << (i * 8);
    }

    return result;
};

var encode_uint = function(assembly, typecode, size, value) {
    // should be the same as encoding an int unless
    // we have to deal with endieness on different archs
    // I'll have to check that
    encode_int(assembly, typecode, size, value);

};

var decode_void = function(assembly, size) {
    if (size != 0)
        throw "Error while decoding a void type.  Expecting size = 0 but got size = " + size;

    return null;
};

var encode_void = function(assembly, typecode, size, value) {
    if (size != 0)
        throw "Error while encoding a void type.  Size must be 0";

    encode_typecode(assembly, typecode);
};

var decode_bool = function(assembly, size) {
    var value = decode_uint(assembly, size);
    if (value)
        return true;
    else
        return false;
};

var encode_bool = function(assembly, typecode, size, value) {
    if (value)
        encode_uint(assembly, typecode, size, 1);
    else
        encode_uint(assembly, typecode, size, 0);
};

var decode_dec = function(assembly, size) {
    var dec = decode_uint(assembly, 1);
    var num = decode_int(assembly, size - 1);
    var result = num / (dec * 10);

    return result;
};

var encode_dec = function(assembly, typecode, size, value) {
    // FIXME: We might need a new class to represent this type
    throw "Not implemented yet!!!"

};

var decode_datetime = function(assembly, size) {
    var epoc = decode_uint(assembly, size);
    var datetime = new Date();
    datetime.setTime(epoc);

    return datetime;
};

var encode_datetime = function(assembly, typecode, size, value) {
    if (value.getTime)
        value = value.getTime();

    encode_uint(assembly, typecode, size, value);
};

var decode_float = function(assembly, size) {
    var dec = decode_uint(assembly, 1);
    var num = decode_int(assembly, size - 1);
    var result = num / (dec * 10);

    return result;
};

var encode_float = function(assembly, typecode, size, value) {
    throw "Not implemented yet!!!"
};

var encode_bit = function(assembly, typecode, size, value) {
    // no-op since bits are special cases which use
    // the packing flags for values
    // special cased in the versioned protocol code
};

var decode_bit = function(assembly, size) {
    // since bits are special cases which use
    // the packing flags for values if this is called
    // it means the bit was set so return 1

    return 1;
};

/************** variable types *******************/
var decode_struct = function(assembly, varsize) {

    var size = decode_uint(assembly, varsize);
    var class_code = decode_uint(assembly, 1);
    var struct_code = decode_uint(assembly, 1);

    var cls = this.lookup_class(class_code);
    var struct = cls.struct_codes[struct_code];

    var result = new struct().decode(assembly);

    return result;
};

var encode_struct = function(assembly, typecode, size, value) {
    throw "Not implemented!!! Struct Encoding";
};

var decode_map = function(assembly, varsize) {
    var result = {};
    var size = decode_uint(assembly, varsize);
    var count = decode_uint(assembly, 4);

    for(var i=0; i < count; i++) {
        var key = decode_str(assembly, 1);
        var typecode = decode_uint(assembly, 1);

        // for container types we assume the marshaler will have a get_type
        // method so we can decode the child types
        var type = this.lookup_type(typecode);
        var value = new type().decode(assembly);
        result[key] = value;
    }

    return result;
};

var encode_map = function(assembly, typecode, size, value) {
    var map_assembly = new Assembly({});
    var count = 0;
    var map_size = 1;

    encode_typecode(assembly, typecode);
    // encode each key/value pair, guessing at the value type
    // if not implicitly specified
    for(var k in value) {
        count++;

        var v = value[k];
        var type = this.guess_type(v);
        encode_str(map_assembly, null, 1, k);
        type.encode(map_assembly);
    }

    map_size += map_assembly.get_size();

    assembly.write(int_to_bytestr(map_size, 4));
    assembly.write(int_to_bytestr(count, 4));
    assembly.write(map_assembly.get_data());
};

var decode_array = function(assembly, varsize) {
    var result = [];
    var size = decode_uint(assembly, varsize);
    var typecode = decode_uint(assembly, 1);
    // for container types we assume the marshaler will have a get_type
    // method so we can decode the child types
    var type = this.lookup_type(typecode);
    var count = decode_uint(assembly, 4);

    for(var i=0; i < count; i++) {
        var value = new type().decode(assembly);
        result.push(value)
    }

    return result;
};

var encode_array = function(assembly, typecode, size, value) {
    throw "Not implemented yet!!!"
};

var decode_str = function(assembly, varsize) {
    var result = '';
    var size = decode_uint(assembly, varsize);
    var result = decode_bin(assembly, size);

    return result;
};

var encode_str = function(assembly, typecode, size, value) {
    var var_size = value.length;
    encode_typecode(assembly, typecode);
    assembly.write(int_to_bytestr(var_size, size));
    assembly.write(value);
};

var decode_seq_set = function(assembly, varsize) {
    var results = [];
    var size = decode_uint(assembly, varsize);
    const mask = 0x0f;
    for (var i=0; i<size; i++) {
        var seq = decode_uint(assembly, 1);
        var lower = seq >> 4;
        var upper = seq & mask;
        results.push([lower, upper]);
    }

    return results;
};

var encode_seq_set = function(assembly, typecode, size, value) {
    throw "Not implemented yet!!!"
};

/******************* higher level constructs **************************/

var encode_header = function(assembly) {
    var header = this.get_header();
    assembly.write(header);
};

var decode_header = function(assembly) {
    var header = {}
    header['id'] = this.decode_bin(assembly, 4);
    if (header['id']!='AMQP')
        throw "Malformed AMQP header";

    header['class'] = this.decode_int(assembly, 1);
    header['instance'] = this.decode_int(assembly, 1);
    header['version_major'] = this.decode_int(assembly, 1);
    header['version_minor'] = this.decode_int(assembly, 1);

    return header;
};

/************* messaging API *******************/

var UNLIMITED = 0xFFFFFFFF;

/*************************************************************************
  Sessions provide a linear context for sending and receiving
  Messages. Messages are sent and received
  using the Sender.send and Receiver.fetch methods of the
  Sender and Receiver objects associated with a Session.

  Each Sender and Receiver is created by supplying either a
  target or source address to the sender and receiver methods of
  the Session. The address is supplied via a string syntax documented
  below.

  Addresses
  =========

  An address identifies a source or target for messages. In its
  simplest form this is just a name. In general a target address may
  also be used as a source address, however not all source addresses
  may be used as a target, e.g. a source might additionally have some
  filtering criteria that would not be present in a target.

  A subject may optionally be specified along with the name. When an
  address is used as a target, any subject specified in the address is
  used as the default subject of outgoing messages for that target.
  When an address is used as a source, any subject specified in the
  address is pattern matched against the subject of available messages
  as a filter for incoming messages from that source.

  The options map contains additional information about the address
  including:

    - policies for automatically creating, and deleting the node to
      which an address refers

    - policies for asserting facts about the node to which an address
      refers

    - extension points that can be used for sender/receiver
      configuration

  Mapping to AMQP 0-10
  --------------------
  The name is resolved to either an exchange or a queue by querying
  the broker.

  The subject is set as a property on the message. Additionally, if
  the name refers to an exchange, the routing key is set to the
  subject.

  Syntax
  ------
  The following regular expressions define the tokens used to parse
  addresses::
    LBRACE: \\{
    RBRACE: \\}
    LBRACK: \\[
    RBRACK: \\]
    COLON:  :
    SEMI:   ;
    SLASH:  /
    COMMA:  ,
    NUMBER: [+-]?[0-9]*\\.?[0-9]+
    ID:     [a-zA-Z_](?:[a-zA-Z0-9_-]*[a-zA-Z0-9_])?
    STRING: "(?:[^\\\\"]|\\\\.)*"|\'(?:[^\\\\\']|\\\\.)*\'
    ESC:    \\\\[^ux]|\\\\x[0-9a-fA-F][0-9a-fA-F]|\\\\u[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]
    SYM:    [.#*%@$^!+-]
    WSPACE: [ \\n\\r\\t]+

  The formal grammar for addresses is given below::
    address = name [ "/" subject ] [ ";" options ]
       name = ( part | quoted )+
    subject = ( part | quoted | "/" )*
     quoted = STRING / ESC
       part = LBRACE / RBRACE / COLON / COMMA / NUMBER / ID / SYM
    options = map
        map = "{" ( keyval ( "," keyval )* )? "}"
     keyval = ID ":" value
      value = NUMBER / STRING / ID / map / list
       list = "[" ( value ( "," value )* )? "]"

  This grammar resuls in the following informal syntax::

    <name> [ / <subject> ] [ ; <options> ]

  Where options is::

    { <key> : <value>, ... }

  And values may be:
    - numbers
    - single, double, or non quoted strings
    - maps (dictionaries)
    - lists

  Options
  -------
  The options map permits the following parameters::

    <name> [ / <subject> ] {
      create: <create-policy>,
      delete: <delete-policy>,
      assert: <assert-policy>,
      node-properties: {
        type: <node-type>,
        durable: <node-durability>,
        x-properties: {
          bindings: ["<exchange>/<key>", ...],
          <passthrough-key>: <passthrough-value>
        }
      }
    }

  The create, delete, and assert policies specify who should perfom
  the associated action:

   - I{always}: the action will always be performed
   - I{sender}: the action will only be performed by the sender
   - I{receiver}: the action will only be performed by the receiver
   - I{never}: the action will never be performed (this is the default)

  The node-type is one of:

    - I{topic}: a topic node will default to the topic exchange,
      x-properties may be used to specify other exchange types
    - I{queue}: this is the default node-type

  The x-properties map permits arbitrary additional keys and values to
  be specified. These keys and values are passed through when creating
  a node or asserting facts about an existing node. Any passthrough
  keys and values that do not match a standard field of the underlying
  exchange or queue declare command will be sent in the arguments map.

  Examples
  --------
  A simple name resolves to any named node, usually a queue or a
  topic::

    my-queue-or-topic

  A simple name with a subject will also resolve to a node, but the
  presence of the subject will cause a sender using this address to
  set the subject on outgoing messages, and receivers to filter based
  on the subject::

    my-queue-or-topic/my-subject

  A subject pattern can be used and will cause filtering if used by
  the receiver. If used for a sender, the literal value gets set as
  the subject::

    my-queue-or-topic/my-*

  In all the above cases, the address is resolved to an existing node.
  If you want the node to be auto-created, then you can do the
  following. By default nonexistent nodes are assumed to be queues::

    my-queue; {create: always}

  You can customize the properties of the queue::

    my-queue; {create: always, node-properties: {durable: True}}

  You can create a topic instead if you want::

    my-queue; {create: always, node-properties: {type: topic}}

  You can assert that the address resolves to a node with particular
  properties::

    my-transient-topic; {
      assert: always,
      node-properties: {
        type: topic,
        durable: False
      }
    }
***********************************************************************/

var AddressParser = Class(function() {
    this.LBRACE = '\\{';
    this.RBRACE = '\\}';
    this.LBRACK = '\\[';
    this.RBRACK = '\\]';
    this.COLON = ':';
    this.SEMI = ';';
    this.SLASH = '/';
    this.COMMA = ',';
    this.NUMBER = '[+-]?[0-9]*\\.?[0-9]+';
    this.ID = '[a-zA-Z_](?:[a-zA-Z0-9_-]*[a-zA-Z0-9_])?';
    this.STRING = '"((?:[^\\\\"]|\\\\.)*)"|' + "'((?:[^\\\\']|\\\\.)*)'";
    this.ESC = '\\\\[^ux]|\\\\x[0-9a-fA-F][0-9a-fA-F]|\\\\u[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]';
    this.SYM = '[.#*%@$^!+-]';
    this.WSPACE = '\\s';

    this.init = function(address) {
        this._raw_address = address;
        this.name = '';
        this.subject = null;
        this.options = {};

        this._parse();
    };

    this.subject_to_filter = function() {
        if (!this.subject)
            return this.subject;

        return this.subject.replace('*', '#', 'g');
    };

    this._parse = function() {
        this.name = this.eat_until(this.SLASH, this.SEMI);

        if (this.starts_with(this.SLASH)) {
            this.eat(this.SLASH);
            this.subject = this.eat_until(this.SEMI);
        }

        if (this.starts_with(this.SEMI)) {
            this.eat(this.SEMI);

            if(this.starts_with(this.LBRACE))
                this.options = this.parse_map();
        }

    };

    this._or = function(args) {
        if (args.length == 0)
            throw "InternalError: Argument list empty to _or";
        var re_str = args.join('|');
        var re = RegExp(re_str);

        return re;
    };

    this.parse_map = function() {
        this.eat(this.LBRACE);

        var result = {};
        while(true) {
            if (this.starts_with(this.NUMBER,
                                 this.STRING,
                                 this.ID,
                                 this.LBRACE,
                                 this.LBRACK)) {
                var kv = this.parse_keyval();

                result[kv[0]] = kv[1];
                if (this.starts_with(this.COMMA))
                    this.eat(this.COMMA);
                else if (this.starts_with(this.RBRACE))
                    break;
                else
                    throw "ParseError: error parsing options map";

           } else if (this.start_with(this.RBRACE)) {
                break;
           } else {
                throw "ParseError: error parsing options map";
           }
        }

        this.eat(this.RBRACE);

        return result;
    };

    this.parse_keyval = function() {
        var key = this.parse_value();
        this.eat(this.COLON);
        var val = this.parse_value();
        return ([key, val]);
    };

    this.parse_value = function() {
        var result = null;
        if (this.starts_with(this.NUMBER)) {
            var v = this.eat(this.NUMBER);
            result = v[0];
        } else if (this.starts_with(this.STRING)) {
            var v = this.eat(this.STRING);
            result = v[1] || v[2];
        } else if (this.starts_with(this.ID)) {
            var v = this.eat(this.ID);
            result = v[0];
        } else if (this.starts_with(this.LBRACE)) {
            result = this.parse_map()
        } else if (this.starts_with(this.LBRACK)) {
            result = this.parse_list()
        } else {
            throw "ParseError: option value in wrong format";
        }

        return result;
    };

    this.parse_list = function() {
        this.eat(this.LBRACK);

        var result = []

        while(true) {
            if (this.starts_with(this.RBRACK))
                break;
            else
                result.push(this.parse_value());

            if (this.starts_with(this.COMMA))
                this.eat(this.COMMA);
            else if (this.starts_with(this.RBRACK))
                break;
            else
                throw "ParseError: list value is in wrong format";
        }

        this.eat(RBRACK)
        return result;
    };

    this.starts_with = function() {
        var args = [];
        for (var i=0; i < arguments.length; i++) {
            args.push('^' + this.WSPACE + '*(?:' + arguments[i] + ')');
        }

        var re = this._or(args);
        var m = this._raw_address.search(re);
        if (m == -1)
            return false;

        return true;
    };

    this.eat = function(token) {
        if (typeof(token) == 'undefined') {
            return this._raw_address;
        }

        var re = RegExp('^' + this.WSPACE + '*(?:' + token + ')');

        var m = this._raw_address.match(re);
        this._raw_address = this._raw_address.replace(re, '');

        return m;
    };

    this.eat_until = function() {
        var addr = this._raw_address;
        var args = Array.prototype.slice.call(arguments);
        var re = this._or(args);

        var m = addr.search(re);

        // no match, return whole string
        if (m == -1) {
            this._raw_address = '';
            return addr;
        }

        var result = addr.substring(0, m);
        this._raw_address = addr.substring(m);
        return result;
    }
});

/* Add this to a test suite at some point
new AddressParser('test');
new AddressParser('test2/wow');
new AddressParser('test3/org.wow;{arg1: 1, "arg2":\'2\'}');
new AddressParser("test4;{\"arg1\": 1, arg2:'2'}");
*/

var Receiver = Class(function(supr) {
    this.init = function(session, index, source, options) {
        this._sess = session;
        this._index = index;
        this.addr = new AddressParser(source);
        this.destination = index + '';
        this._incoming = [];
        this._paused = false;
        this._dispatch_timer = null;
        this.onReady = null;
        this._grant_pending = true;
    };

    this._dispatch = function() {
        if(this.onReady && this._incoming.length)
            this.onReady(this);

        if(!this.onReady || !this._incoming.length) {
            window.clearInterval(this._dispatch_timer);
            this._dispatch_timer = null;
        }
    };

    this._queue_message = function(msg) {
        this._incoming.push(msg);
        if(!this._paused && !this._dispatch_timer && this.onReady)
            this._dispatch_timer = window.setInterval(bind(this, this._dispatch), 1);

    };

    this.capacity = function(cap) {
        if(cap==null)
            cap = UNLIMITED;

        if (typeof(cap) != 'undefined') {
            this._capacity = cap;
            this._grant_pending = true;
        } else {
            return this._capacity;
        }
    };

    this.pending = function() {
        return this._incoming.length;
    };

    this.fetch = function() {
        return this._incoming.pop();
    };

    this.pause = function() {
        if (this._paused)
            return;

        this._paused = true;
        if(this._dispatch_timer) {
            window.clearInterval(this._dispatch_timer);
            this._dispatch_timer = null;
        }
    };

    this.play = function() {
        if (!this._paused)
            return;

        ths._paused = false;
        if(this._incoming && this.onReady)
            this._dispatch_timer = window.setInterval(bind(this, this._dispatch), 1);
    };

    this.close = function() {

    };
});

var Sender = Class(function(supr) {
    this.init = function(session, index, target, options) {
        this._sess = session;
        this._index = index;
        this._messages = [];
        this._dispatch_timer = null;
        this.addr = new AddressParser(target);
        this._ready = false;

    };

    this.pending = function() {
        return this._messages;
    };

    this.send = function(msg_obj, sync) {
        if (typeof(sync) == 'undefined')
            sync = true;

        this._messages.push(msg_obj);

        if (sync) {
            this.sync();
        } else {
            if(!this._dispatch_timer)
                this._dispatch_timer = window.setInterval(bind(this, this._dispatch), 1);
        }

    };

    this._dispatch = function(flush) {
        //if we are not ready we can't send even if sync==true
        if (!this._ready)
            return;

        if (this._messages.length == 0 && this._dispatch_timer) {
            window.clearInterval(this._dispatch_timer);
            this._dispatch_timer == null;
            return;
        }

        var send_list = this._messages;
        if(!flush)
            send_list = [this._messages.pop()]; // send 1

        while (send_list.length)
            this._dispatch_one(this._construct_transfer(send_list.pop()));

        if (this._messages.length == 0 && this._dispatch_timer) {
            window.clearInterval(this._dispatch_timer);
            this._dispatch_timer = null;
        }
    }

    this.sync = function() {
        this._dispatch(true);
    };

    this.close = function() {

    };

    this._construct_transfer = function() {
       // override this in the versioned plugin
    };

    this._dispatch_one = function(msg) {
       // override this in the versioned plugin
    };
});

exports.Receiver = Receiver;
exports.Sender = Sender;
exports.DefaultsClass = DefaultsClass;
exports.Assembly = Assembly;
exports.Message = Message;
exports.deep_copy_defaults = deep_copy_defaults;
exports.extend = extend;
exports.register = register;
exports.get_connection = get_connection;

exports.int_to_bytestr = int_to_bytestr;
exports.decode_typecode = decode_typecode;
exports.encode_typecode = encode_typecode;
exports.decode_bin = decode_bin;
exports.encode_bin = encode_bin;
exports.decode_int = decode_int;
exports.encode_int = encode_int;
exports.decode_uint = decode_uint;
exports.encode_uint = encode_uint;
exports.decode_void = decode_void;
exports.encode_void = encode_void;
exports.decode_bool = decode_bool;
exports.encode_bool = encode_bool;
exports.decode_dec = decode_dec;
exports.encode_dec = encode_dec;
exports.decode_datetime = decode_datetime;
exports.encode_datetime = encode_datetime;
exports.decode_float = decode_float;
exports.encode_float = encode_float;
exports.encode_bit = encode_bit;
exports.decode_bit = decode_bit;

exports.decode_struct = decode_struct;
exports.encode_struct = encode_struct;
exports.decode_map = decode_map;
exports.encode_map = encode_map;
exports.decode_array = decode_array;
exports.encode_array = encode_array;
exports.decode_str = decode_str;
exports.encode_str = encode_str;
exports.decode_seq_set = decode_seq_set;
exports.encode_seq_set = encode_seq_set;

exports.encode_header = encode_header;
exports.decode_header = decode_header;
exports.UNLIMITED = UNLIMITED;

})();

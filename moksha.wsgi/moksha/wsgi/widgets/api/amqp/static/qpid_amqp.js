(function(){
jsio("from amqp.protocol import DefaultsClass, get_connection, UNLIMITED");
jsio("import Class, bind");
jsio("import jsio.logging");

var logger = jsio.logging.getLogger('QpidAmqp');

var Session = Class(function() {
    this.init =  function(connection, name, transactional) {
        this.name = name;
        this._sess_driver = connection._session_driver(this.name);
        this._conn = connection;

        this._transactional = transactional;

        this._committing = false
        this._committed = true
        this._aborting = false
        this._aborted = false

        this._last_channel = -1;
        this._receivers = [];
        this._senders = [];
        this._unacked = [];
        this._acked = [];
        this._ack_capacity = UNLIMITED;

        this.error = null;
        this.closing = false;
        this.closed = false;

        var name_re = new RegExp(name + '\\..*');
        var _this = this;

        var handle_transfer = function(msg) {
            /* FIXME: How do we determine which session
                      we are coming from
            if (!dest)
                return false;
            */

            _this._dispatch(msg);
            return true;
        };

        this._conn._conn_driver.subscribe('message',
                                          'transfer',
                                          null,
                                          handle_transfer,
                                          false);

    };

    this._dispatch = function(msg) {
        /* FIXME: connection should be dispatching
                  since we might have multiple sessions
                  and we need to get the headers before we
                  know which session to send to
        */
        var d = msg.get('destination');
        var index = parseInt(d);
        this._receivers[index]._queue_message(msg);
    };

    this.Message = function() {this._sess_driver.Message.apply(this._sess_driver, arguments)};
    this.Queue = function() {this._sess_driver.Queue.apply(this._sess_driver, arguments)}
    this.Exchange = function() {this._sess_driver.Exchange.apply(this._sess_driver, arguments)};

    this.get_next_channel = function() {
        this._last_channel++;
        return this._last_channel;
    };

    this.receiver = function(address, options) {
        var index = this._receivers.length;
        var r = new this._sess_driver.Receiver(this, index, address, options);
        this._receivers.push(r);

        return r;
    };

    this.sender = function(address, options) {
        var index = this._senders.length;
        var s = new this._sess_driver.Sender(this, index, address, options);
        this._senders.push(s);

        return s;
    };

 });

var Connection = Class(function() {

    this.init = function(options) {
        this.version = options.version;
        this._conn_driver = get_connection(this.version, options);
    };

    this.create_session = function(name, transactional) {
        if (typeof(transactional) == undefined)
            transactional = false;

        return new Session(this, name, transactional);
    };

    this.session = this.create_session;

    this._session_driver = function(name) {
        return this._conn_driver.create_session(name);
    };

    this.start = function() {
        this._conn_driver.start();
    };
});

exports.Session = Session;
exports.Connection = Connection;

})();
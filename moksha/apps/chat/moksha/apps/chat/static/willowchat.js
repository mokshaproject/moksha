(function() {

Orbited.settings.streaming = true

if (window.addEventListener) {
    window.addEventListener('load', function() { WillowChat.util.setup(); }, false);
}
else if (window.attachEvent) {
    window.attachEvent('onload', function() { WillowChat.util.setup(); });
}


if (!window.WillowChat) {
    WillowChat = {}
}
WillowChat.settings = {}
WillowChat.settings.hostname = document.domain
WillowChat.settings.port = (location.port.length > 0) ? location.port : 80
WillowChat.settings.defaultTheme = 'simple'
WillowChat.settings.client = 'irc'
WillowChat.clients = {}
WillowChat.clients.map = {}
WillowChat.util = {}


if (!WillowChat.guis) {
    WillowChat.guis = {}
}
if (!WillowChat.guis.map) {
    WillowChat.guis.map = {}
}

if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function(n) {
        for (var i = 0; i < this.length; ++i) {
            if (this[i] === n) {
                return i
            }
        }
        return -1
    }
}




WillowChat.util.setup = function() {
    // TODO: first setup from remote and url
    // TODO: this is a *really* ugly way to do this... Fix it

    try {
        var i = location.href.indexOf('&opts=')
        var opts = JSON.parse(unescape(location.href.slice(i+6)))
    }
    catch(e) {
        // If the options aren't there, then someone must be trying to use this
        // library manually, which we want to allow.
        return
    }
    // TODO: we actually need to get the "backend" hostname value
    WillowChat.settings.hostname = 'localhost'
    var client = new WillowChat.clients.map[WillowChat.settings.client](opts)
    var gui = new WillowChat.guis.map[opts.theme ? opts.theme : WillowChat.settings.defaultTheme](client, opts)

    return gui
}





WillowChat.BaseClient = function() {
    var self = this;
    self.readyState = self.READY_STATE_INITIALIZED;
    self.onUsernameTaken = function() { };
    self.onConnect = function() { };
    self.onPresence= function() { };
    self.onDisconnect = function() { };
    self.onMessage = function() { };
    self.onJoin = function() { };
    self.onLeave = function() { };
    self.onAction = function() { };
    self.onRename = function() { };
}

WillowChat.BaseClient.prototype.connect = function(options) {
    var self = this;
    if (!this.doConnect) {
        throw new Error("NotImplemented");
    }
    var username = options.username
    if (!username) {
        throw new Error("Missing username")
    }
    var roomId = options.roomId ? options.roomId : self.opts.roomId
    if (!roomId) {
        throw new Error("Missing roomId")
    }
    var hostname = options.hostname
    var port = options.port
    if (!port) {
        port = 6667
    }
    if (!hostname) {
        if (!self.opts.addr) {
            throw new Error("missing connection information");
        }
        hostname = self.opts.addr[0]
        port = self.opts.addr[1]
    }
    return self.doConnect(username, roomId, hostname, port);
};
WillowChat.BaseClient.prototype.rename = function(newName) {
    throw new Error("NotImplemented");
};
WillowChat.BaseClient.prototype.sendMessage = function(msg) {
    throw new Error("NotImplemented");
};
WillowChat.BaseClient.prototype.sendAction = function(action) {
    throw new Error("NotImplemented");
};
WillowChat.BaseClient.prototype.disconnect = function() {
    throw new Error("NotImplemented");
};
WillowChat.BaseClient.prototype.READY_STATE_INITIALIZED = 0;
WillowChat.BaseClient.prototype.READY_STATE_CONNECTING = 1;
WillowChat.BaseClient.prototype.READY_STATE_CONNECTED = 2;
WillowChat.BaseClient.prototype.READY_STATE_DISCONNECTED = 3;


WillowChat.clients.IRCClient = function(opts) {
    var self = this;
    self._conn = null;
    self.opts = opts
};

WillowChat.clients.IRCClient.prototype = new WillowChat.BaseClient();

WillowChat.clients.IRCClient.prototype.logger = Orbited.getLogger('WC.c.IRCClient');
WillowChat.clients.map.irc = WillowChat.clients.IRCClient

WillowChat.clients.IRCClient.prototype.disconnect = function() {
    var self = this;
    if (self.readyState == self.READY_STATE_DISCONNECTED) {
        return
    }
    self.readyState = self.READY_STATE_DISCONNECTED;
    // TODO: would be nice to have a quit message or something
    self._conn.reset()
    self._conn = null;
    self.onDisconnect()
}


WillowChat.clients.IRCClient.prototype.doConnect = function(username, roomId, hostname, port) {
    var self = this;
    self.username = username
    self.roomId = roomId;
    if (self.roomId[0] != '#') {
        self.roomId = '#' + self.roomId
    }
    self._conn = new IRCClient()
    self.presence = []
    var irc = self._conn
    // By default, assume the irc server is on the same host as the willowchat
    // server

    function parseName(identity) {
        // TODO remove privileges from name head.
        return identity.split("!", 1)[0];
    }
    irc.onclose = function() {
        self.disconnect();
    }
    irc.onopen = function() {
        irc.ident(self.username, '8 *', self.username);
        irc.nick(self.username);
    }
;;; self.logger.debug('do irc.connect', hostname, port)
    irc.connect(hostname, port)
    self.readyState = self.READY_STATE_CONNECTING

    irc.onJOIN = function(command) {
;;;     self.logger.debug('irc.onJOIN', command)
        // Ignore initial onJoin (before names)
        var joiner = parseName(command.prefix)
;;;     self.logger.debug('irc.onJoin.a')
        self.logger.debug('self.presence', self.presence, Orbited.JSON.stringify(self.presence))
        if (self.presence.indexOf(joiner) == -1) {
;;;     self.logger.debug('irc.onJoin.b')
            self.presence.push(joiner)
        }
;;;     self.logger.debug('irc.onJoin.c')
        if (self.readyState == self.READY_STATE_CONNECTED) {
;;;     self.logger.debug('irc.onJoin.d')
            self.onJoin(joiner);
        }
;;;     self.logger.debug('irc.onJoin.e')
    }
    irc.onPART = irc.onQUIT = function(command) {
        var leaver = parseName(command.prefix);
        var message = command.args.join(" ");
        var i = self.presence.indexOf(leaver)
        if (i != -1) {
            self.presence.splice(i,1)
        }
        self.onLeave(leaver);
    }
    irc.onNICK = function(command) {
        // See http://tools.ietf.org/html/rfc2812#section-3.1.2
        var previousNick = parseName(command.prefix);
        var i = self.presence.indexOf(previousNick)
        if (i != -1) {
            self.presence.splice(i,1)
        }
        var newNick = command.args[0];
        if (self.presence.indexOf(newNick) == -1) {
            self.presence.push(newNick)
        }
        self.onPresence()
    };

    irc.onPRIVMSG = function(command) {
        var sender = parseName(command.prefix);
        var target = command.args[0];
        var message = command.args[1];
        self.onMessage(sender, message);
    }
    irc.onACTION = function(command) {
;;;     self.logger.debug('irc.onACTION', command)
        var sender = parseName(command.prefix);
        var message = command.args.slice(1).join(" ")
        self.onAction(sender, message);
    }

    irc.onresponse = function(command) {
        self.logger.debug('onresponse', command)
        var responseCode = parseInt(command.type);
        if (responseCode == 353) {
            // 353 is the code for RPL_NAMEREPLY.

            // The args are:
            //
            // """
            //   <target> ( "=" / "*" / "@" ) <channel>
            //    :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )
            //
            //   - "@" is used for secret channels, "*" for private
            //     channels, and "=" for others (public channels).
            // """ -- rfc2812
            var channel = command.args[2];
            if (channel != self.roomId)
                return;
            var partialUserList = command.args[3].split(' ');
            for (var i = 0, l = partialUserList.length; i < l; ++i) {
                // trim the name
                var name = partialUserList[i].replace(/^\s+|\s+$/g,"");
                if (name[0] == '@' || name[0] == '+') {
                    name = name.slice(1);
                }
                if (name == "" || self.presence.indexOf(name) != -1) {
                    continue;
                }
                self.presence.push(name)
            }
        }
        else if (responseCode == 366) {
        // 366 is the code for RPL_ENDOFNAMES.
            self.readyState = self.READY_STATE_CONNECTED
            self.onConnect();
        }
        else if (responseCode == 376) {
        //  376     RPL_ENDOFMOTD
        //  :End of /MOTD command"
            irc.join(self.roomId);
        }
    }
    irc.onerror = function(command) {
        self.logger.debug('onerror', command)
        var responseCode = parseInt(command.type);
        if (responseCode == 431 || responseCode == 432 || responseCode == 433) {
        // 431     ERR_NONICKNAMEGIVEN
        // 432     ERR_ERRONEUSNICKNAME
        // 433     ERR_NICKNAMEINUSE
            self.onUsernameTaken();
        }
/*        else if (responseCode == 451) {
        // 451 is the code for ERR_NOTREGISTERED
        // Probably means the nick we chose was taken
        }
*/
    }
}
WillowChat.clients.IRCClient.prototype.rename = function(newUserName) {
    var self = this;
    var irc = self._conn;
    switch(self.readyState) {
        case self.READY_STATE_CONNECTING:
        case self.READY_STATE_CONNECTED:
            irc.nick(newUserName);
            self.userName = newUserName;
            break;
        default:
            throw new Error("invalid readyState")
    }
}

WillowChat.clients.IRCClient.prototype.sendMessage = function(msg) {
    var self = this;
    if (self.readyState != self.READY_STATE_CONNECTED) {
        throw new Error('invalid readyState: ' + self.readyState);
    }
    var irc = self._conn;
    irc.privmsg(self.roomId, msg);
}

WillowChat.clients.IRCClient.prototype.sendAction = function(action) {
    var self = this;
    if (self.readyState != self.READY_STATE_CONNECTED) {
        throw new Error('invalid readyState: ' + self.readyState);
    }
    var irc = self._conn;
    irc.action(self.roomId, action);
}


var createXHR = function () {
    try { return new XMLHttpRequest(); } catch(e) {}
    try { return new ActiveXObject('MSXML3.XMLHTTP'); } catch(e) {}
    try { return new ActiveXObject('MSXML2.XMLHTTP.3.0'); } catch(e) {}
    try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
    try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
    throw new Error('Could not find XMLHttpRequest or an alternative.');
}


})()

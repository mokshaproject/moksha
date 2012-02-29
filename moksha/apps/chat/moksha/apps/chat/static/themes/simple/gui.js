(function() {

if (!window.WillowChat) {
    console.log('no willochat found in gui?');
    Willowchat = {}
}

if (!WillowChat.guis) {
    WillowChat.guis = {}
}

if (!WillowChat.guis.map) {
    WillowChat.guis.map = {}
}
var ENTER_KEY = 13
WillowChat.guis.map.simple = WillowChat.guis.SimpleGui = function(wc, opts) {
    var self = this;
    self.presenceShown = true;
    var logger = Orbited.getLogger('WillowChatTest');
//    logger.enabled = true;
    var username = null;
    var presence = {}

    $('#nickname').focus();
    $('#nickname').keypress( function(e) {
        var key = e.charCode || e.keyCode || 0
        if (key == ENTER_KEY) {
            self.connect();
        };
    });
    $('#chatboxInput').keypress(function(e) {
        var key = e.charCode || e.keyCode || 0;
        if (key == ENTER_KEY) {
        self.sendMessage();
        return false;
        };
    });
    $("#popupContent p").html(opts.greeting)
    $("#presenceToggle").click(function() {
        if (self.presenceShown) {
            self.presenceShown = false;
            $("#presence").hide()
            $("#presenceToggle").html('&larr;');
        }
        else {
            self.presenceShown = true;
            $("#presence").show();
            $("#presenceToggle").html('&rarr;');
        }
        if (wc.readyState == wc.READY_STATE_CONNECTED) {
            $('#chatboxInput').focus();
        }
        else {
            $('#nickname').focus();
        }
    })
    var scrollDown = function() {
      var box = $('#history')[0]
      box.scrollTop = box.scrollHeight;
    }
    var isSubstring = function (sub, str) {
    // case insensitive substring test
        return str.toLowerCase().indexOf(sub.toLowerCase()) >= 0;
    };
    var sanitize = (function(str) {
    // See http://bigdingus.com/2007/12/29/html-escaping-in-javascript/
        var MAP = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        var repl = function(c) { return MAP[c]; };
        return function(s) {
            return s.replace(/[&<>'"]/g, repl);
        };
    })();

    // TODO: test this out
    var userRenamed = function(oldname, newname) {
        $("<div class='informative rename'></div>")
            .html("<span class='user'>" + oldname + "</span> is now known as " +
                "<span class='user'>" + newname + "</span>")
            .appendTo("#history");
        scrollDown();
        $("#user_" + oldname)
            .attr("id", "user_" + newname)
            .html(newname);
    }

    var addName = function (name) {
        presence[name] = 1
        $('<div class="user_entry" id="user_' + name + '">' + name + '</div>')
            .appendTo("#presenceList");
    };

    var removeName = function (name) {
        delete presence[name];
        $(".user_list #user_" + name).remove()
    };

    var sortNames = function () {
        $('#presenceList').empty();
        var list = [];
        for (var user in presence) {
            list.push(user);
        };
        list.sort()
        for (var i=0; i < list.length; i++) {
            var user = list[i];
            $('<div class="user_entry" id="user_' + user + '">' + user + '</div>')
                .appendTo("#presenceList");
        };
    };
    self.connect = function() {
        username = $("#nickname").val();
        if (!username) {
            logger.debug('please enter a username');
            return
        }
        $('#popup, #absorbClicks').hide();
        $('#chatboxInput').focus();
        $('#chatboxInput').val('')

        connected = true;
        wc.connect( {
            username: username
        })
        wc.onConnect = function(data) {
            /* This is somewhat important -- without this IE can run into some
             * issues with reconnecting
             */

            window.onbeforeunload = function() {
                if (wc.readyState == wc.READY_STATE_CONNECTED) {
                return 'Are you sure you want to quit and lose the chat connection?';
                }
            };
            window.onunload = function() {
                if (wc.readyState == wc.READY_STATE_CONNECTED) {
                    wc.disconnect();
                }
           }


            $("<div class='informative'>Entered ChatRoom</div>").appendTo("#history");
            for (var i = 0; i < wc.presence.length; ++i) {
                addName(wc.presence[i]);
            }
            sortNames();
            logger.debug('connected', data, wc.presence)
        }
        wc.onMessage = function(sender, message) {
            logger.debug('msg', sender, message);
            var messagediv = $('<div class="message"></div>');

            if (sender == username) {
                messagediv.addClass("self");
            }
            if (isSubstring(username, message)) {
                messagediv.addClass("mentioned");
            }
            messagediv.html('<span class="user">' + sender + ':</span> ' +
                            sanitize(message))
            .appendTo("#history");
            scrollDown();
        }
        wc.onAction = function(s, m) { logger.debug('action', s, m); }

        wc.onJoin = function(joiner) {
            logger.debug('join', joiner);
            addName(joiner);
            sortNames();
            $("<div class='informative join'></div>")
                .html("<span class='user'>" + joiner + '</span> has joined')
                .appendTo("#history");
            scrollDown();
        }
        wc.onLeave = function(leaver) {
            logger.debug('leave', leaver);
            removeName(leaver);
            $("<div class='informative part'></div>")
                .html("<span class='user'>" + leaver + '</span> left')
                .appendTo("#history");
            scrollDown();
        }
        wc.onDisconnect = function() { logger.debug('disconneted'); }
        wc.onUsernameTaken = function() {
            logger.debug('onUsernameTaken', username);
            username += '_'
            try {
                wc.rename(username);
                logger.debug('rename sent');
            }
            catch(e) {
                logger.debug('rename failed:', e)
            }
        }
    }
    self.sendMessage = function() {
        var msg = $('#chatboxInput').val();
        wc.sendMessage(msg)
        $('#chatboxInput').val('');
        // the WillowChat server will not echo our message back, so simulate a send.
        wc.onMessage(username, msg)
    }
    self.sendAction = function() {
        var msg = getMessage()
        wc.sendAction(msg);
        logger.debug('action', username, msg)
    }

}
})()


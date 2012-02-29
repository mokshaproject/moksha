

if (!window.WillowChat) {
    Willowchat = {}
}

if (!WillowChat.guis) {
    WillowChat.guis = {}
}

if (!WillowChat.guis.map) {
    WillowChat.guis.map = {}
}

var willowConnection = null;
WillowChat.guis.map.dojo = WillowChat.guis.DojoGui = function(wc, opts) {
  console.log("Neat? ", wc, opts);
 willowConnection = wc;
}

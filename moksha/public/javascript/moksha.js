/*
 * Moksha javascript library
 *
 * Copyright (c) 2008 Red Hat, Inc.
 *
 * GPLv2+ license.
 *
 * Depends:
 *      jquery.js
 */


(function(){

True = true
False = false
// prevent double loading
if (!(typeof(moksha) === 'undefined'))
    return;

var _moksha_page_scripts_cache = {};

var _moksha_init = false;
// preload cache

$(document).ready(function(){
  _moksha_init = true;
  var $s = $('script[src]');

  $.each($s, function(i, a) {
                var $a = $(a);
                var src = $a.attr('src');
                // for right now just compare exact source values
                // later we will want to be a bit smarter
                if(!_moksha_page_scripts_cache[src]) {
                    _moksha_page_scripts_cache[src] = true;
                }
             }
         );

});

moksha = {
    /******************************************************************
     * Filter the script tags in a fragment of HTML or jQuery DOM
     * so that they aren't double loaded.  You should send in HTML
     * if possible because placing script tags in a jQuery DOM can
     * cause them to load if not done correctly
     ******************************************************************/
    filter_scripts: function(fragment) {
        // don't append to a tag, doing so will cause scripts to load
        if (!fragment.jquery)
            fragment = $(fragment);

        var $stripped = [];
        $.each(fragment, function(i, s) {
            var $s = $(s)
            if ($s.is('script[src]')){
                var src = $s.attr('src');
                //strip query string
                src = src.split('?')[0];

                if(!_moksha_page_scripts_cache[src]) {
                    // we can add more attributes later
                    // right now just set to true
                    _moksha_page_scripts_cache[src] = true;
                    $stripped.push(s);
                }
            } else {
                $stripped.push(s);
            }
        });

        return $stripped;
    },

    /******************************************************************
     * Filter resources in a fragment of HTML or jQuery DOM
     * so that they aren't double loaded.  Right now this is only
     * scripts but could be expanded to css and other loaded
     * resource types. You should send in HTML
     * if possible since loading into a jQuery DOM can cause them
     * to load if not done correctly
     ******************************************************************/
    filter_resources: function(fragment) {
        if (!fragment.jquery)
            fragment = $(fragment);

        var $div = $('<div />');
        var $f = moksha.filter_scripts(fragment);

        return $f;
    },

    /********************************************************************
     * Take a url and attach the csrf hash if available
     ********************************************************************/
    csrf_rewrite_url: function(url) {
        if (typeof(moksha_csrf_token) === 'undefined' || !moksha_csrf_token)
            return url;

        var ourl = moksha.parseUri(url);

        var proto = ourl.protocol;
        if (proto)
             proto += '://';
        var newurl = proto + ourl.authority + ourl.path;
        var qlist = []
        ourl.queryKey['_csrf_token'] = moksha_csrf_token;
        for (q in ourl.queryKey) {
            qlist.push(q + '=' + ourl.queryKey[q]);
        }

        var query = qlist.join('&')
        newurl += '?'+ query;

        if (ourl.anchor)
            newurl += '#' + ourl.anchor;

        return newurl;

    },

    /*
     * modified from parseUri 1.2.1 Steven Levithan <stevenlevithan.com>
     */
    parseUri: function (str) {
        var options = {
            strictMode: false,
            key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
            q:   {
                name:   "queryKey",
                parser: /(?:^|&)([^&=]*)=?([^&]*)/g
            },
            parser: {
                strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*):?([^:@]*))?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
                loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*):?([^:@]*))?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
            }
        };

        var o   = options,
            m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
            uri = {},
            i   = 14;

        while (i--) uri[o.key[i]] = m[i] || "";

        uri[o.q.name] = {};
        uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
            if ($1) uri[o.q.name][$1] = $2;
        });

        return uri;
    },

}

})();
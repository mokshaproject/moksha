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

        var $f = moksha.filter_scripts(fragment);

        return $f;
    },

    /********************************************************************
     * Take a url and attach the csrf hash if available
     ********************************************************************/
    csrf_rewrite_url: function(url, params) {
        var ourl = moksha.parseUri(url);

        if (typeof(params) == 'undefined')
            params = {};

        if (typeof(moksha_csrf_token) != 'undefined' && moksha_csrf_token)
            params['_csrf_token'] = moksha_csrf_token;

        ourl.update_query_string(params);

        return ourl.toString();

    },

    /*********************************************************************
     * Take a form element and add or update a hidden field for the
     * csrf token
     *
     * Example:
     *   <form action="/process_form/"
     *         onSubmit="moksha.csrf_add_form_field(this)">
     *********************************************************************/
    csrf_add_form_field: function(form_element) {
        // do nothing if we don't actually have a token
        if (typeof(moksha_csrf_token) === 'undefined' || !moksha_csrf_token)
            return;

        var $fe = $(form_element);
        var $csrf_field = $("input[name=_csrf_token]", form_element);

        // create a field if it doens't already exist
        if ($csrf_field.length < 1) {
            $csrf_field = $("<input type='hidden'></input>").attr("name", "_csrf_token");

            $fe.append($csrf_field);
        }

        $csrf_field.attr("value", moksha_csrf_token);
    },

    /********************************************************************
     * Take a url and target, attach the csrf hash if available and load
     *
     * FIXME: target is ignored for now
     *
     * TODO: Fast loading where we just switch tabs
     ********************************************************************/
    goto: function(url, params, target) {
        if (typeof(params) != 'object')
            params = {}

        window.location.href = moksha.csrf_rewrite_url(url, params);
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

        var uriClass = function(){};
        uriClass.prototype = {
            update_query_string :function(params) {
               for (p in params)
                   this.queryKey[p] = params[p];
            },

            toString: function() {
                var proto = this.protocol;
                if (proto)
                    proto += '://';

                var url = proto + this.authority + this.path;
                var qlist = []

                for (q in this.queryKey) {
                    qlist.push(q + '=' + this.queryKey[q]);
                }

                var query = qlist.join('&')
                url += '?'+ query;

                if (this.anchor)
                    url += '#' + this.anchor;

                return url;
           }
        };

        var o   = options,
            m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
            uri = new uriClass,
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

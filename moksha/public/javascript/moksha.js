/*
 * Moksha javascript library
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
var _moksha_page_links_cache = {};

var _moksha_init = false;
// preload cache

$(document).ready(function(){
  _moksha_init = true;
  var $s = $('script[src]');
  var $l = $('link[href]');

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

  $.each($l, function(i, a) {
                var $a = $(a);
                var href = $a.attr('href');
                // for right now just compare exact source values
                // later we will want to be a bit smarter
                if(!_moksha_page_links_cache[href]) {
                    _moksha_page_links_cache[href] = true;
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
     * Filter the link tags in a fragment of HTML or jQuery DOM
     * so that they aren't double loaded.
     ******************************************************************/
    filter_links: function(fragment) {
        // don't append to a tag, doing so will cause scripts to load
        if (!fragment.jquery)
            fragment = $(fragment);

        var $stripped = [];
        $.each(fragment, function(i, s) {
            var $s = $(s)
            if ($s.is('link[href]')){
                var href = $s.attr('href');
                //strip query string
                href = href.split('?')[0];

                if(!_moksha_page_links_cache[href]) {
                    // we can add more attributes later
                    // right now just set to true
                    _moksha_page_links_cache[href] = true;
                    $stripped.push(s);
                }
            } else {
                $stripped.push(s);
            }
        });

        return $stripped;
    },

    /******************************************************************
     * Filter anchors in a fragment of HTML or jQuery DOM marked with
     * a moksha_url attribute so that they have updated static links
     * (e.g. run moksha.url on them) and dynamic moksha.goto links
     *
     * Dynamic links will eventually be able to load the correct tabs
     * on click and static links are used when the user opens the link
     * in another browser window.
     *
     * moksha_url="dynamic" - make both a dynamic and static link
     * moksha_url="static" - only make a static link
     ******************************************************************/
    update_marked_anchors: function(fragment) {
        if (!fragment.jquery)
            fragment = $(fragment);

        // get all anchors with a moksha_url attr but not inside a rowtemplate
        var $a_list = $('a[moksha_url]:not(.rowtemplate *):not(.template *)', fragment);

        // run over all the toplevel arguments and add them to the list
        // if they match
        var $filtered_fragment = fragment.filter('a[moksha_url]');
        $a_list.extend($filtered_fragment);

        if (!$a_list.length)
            return fragment;

        var _goto = function(e) {
           var href = $(this).data('dynamic_href.moksha');
           moksha.goto(href);

           return false;
        }

        $.each($a_list, function(i, e) {
                            var $e = $(e)
                            var href = $e.attr('href');
                            var moksha_url = $e.attr('moksha_url');

                            if (moksha_url.toLowerCase() == 'dynamic') {
                                $e.data('dynamic_href.moksha', href);
                                $e.unbind('click.moksha').bind('click.moksha', _goto);
                            }

                            href = moksha.url(href);
                            e.href = href;
                        }
              );

       return fragment;
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
        $f = moksha.filter_links($f);
        $f = moksha.update_marked_anchors($f);
        return $f;
    },

    /********************************************************************
     * Take a url and attach the csrf hash if available
     ********************************************************************/
    csrf_rewrite_url: function(url, params) {
        var purl = moksha.parseUri(url);

        moksha.csrf_rewrite_uri(purl, params);

        return purl.toString();
    },

    csrf_rewrite_uri: function(uri, params) {
        if (typeof(params) == 'undefined')
            params = {};

        if (typeof(moksha_csrf_token) != 'undefined' && moksha_csrf_token)
            params['_csrf_token'] = moksha_csrf_token;

        uri.update_query_string(params);

        return uri;
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

        moksha.add_hidden_form_field(form_element,
                                     '_csrf_token',
                                     moksha_csrf_token);
    },

    /*********************************************************************
     * Take a form element and add or update a hidden field
     *
     * Example:
     *   <form action="/process_form/"
     *         onSubmit="moksha.add_hidden_form_field(this)">
     *
     * Params:
     *   form_element - the form being updated
     *   key - the name of the field we are adding
     *   value - the value to set it to
     *   override_existing - defaults to true, if set to false we only
     *                       add the field if it does not exist or is
     *                       set to an empty string
     *********************************************************************/
     add_hidden_form_field: function(form_element, key, value, override_existing) {
        if (typeof(override_existing) === 'undefined')
            override_existing = true;

        var $fe = $(form_element);
        var $field = $("input[name=" + key + "]", form_element);

        // create a field if it doens't already exist
        if ($field.length < 1) {
            $field = $("<input type='hidden'></input>").attr("name", key);

            $fe.append($field);
        }

        var v = $field.attr("value");
        if (!override_existing && v)
            return;

        $field.attr("value", value);
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

        window.location.href = moksha.url(url, params);
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
            type: 'uri',

            _normalize_path: function(path) {
                // make sure we don't have multiple slashes
                var slashes = /\/+/g;
                path = path.replace(slashes, '/');

                return path;
            },

            prepend_base_url: function(base_url) {
                // make sure we haven't already prepended the base url
                // always remove leading slashes
                var leading_slashes = /^\/+/;

                var base_split = base_url.replace(leading_slashes, '').split('/');
                var dir_split = this.directory.replace(leading_slashes, '').split('/');

                var should_exit = true;
                for (i in base_split) {

                    try {
                        var b = base_split[i];
                        var d = dir_split[i];
                    } catch (e) {
                        should_exit = false;
                        break;
                    }

                    if (b != d) {
                        should_exit = false;
                        break;
                    }
                }

                if (should_exit)
                    return;

                this.directory = base_url + this.directory;
                this.directory = this._normalize_path(this.directory);

                this.relative = this.directory + this.file;
                this.path = this.relative;
            },

            update_query_string: function(params) {
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
                    var value = this.queryKey[q]
                    if (typeof(value) == 'string') {
                        qlist.push(q + '=' + value);
                    } else {
                        // must be a list, break up into seperate query elements
                        for (i in value) {
                            qlist.push(q + '=' + value[i]);
                        }
                    }
                }

                var query = qlist.join('&')
                if(query)
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
            if ($1) {
                var value = uri[o.q.name][$1];
                if (value) {
                    if (typeof(value) === 'string')
                        value = [value];

                    value.push($2);
                    uri[o.q.name][$1] = value;
                } else {
                    uri[o.q.name][$1] = $2;
                }
            }
        });

        return uri;
    },

    connector_load: function(resource, method, params, callback, $overlay_div, loading_icon) {
        var path = moksha.url('/moksha_connector/' + resource + '/' + method);

        return moksha.json_load(path, params, callback, $overlay_div, loading_icon);
    },

    json_load: function(path, params, callback, $overlay_div, loading_icon) {
       return moksha.ajax_load(path, params, callback, $overlay_div, 'json', loading_icon);
    },

    xml_load: function(path, params, callback, $overlay_div, loading_icon) {
       return moksha.ajax_load(path, params, callback, $overlay_div, 'xml', loading_icon);
    },

    html_load: function(path, params, callback, $overlay_div, loading_icon) {
       return moksha.ajax_load(path, params, callback, $overlay_div, 'html', loading_icon);
    },

    ajax_load: function(path, params, callback, $overlay_div, data_type, loading_icon) {
       self = this;

       if (typeof(params) == 'string') {
         params = $.secureEvalJSON(params);
       }

       var profile_start_time = 0;
       if (typeof(moksha_profile)!='undefined' && moksha_profile) {
           var date = new Date()
           profile_start_time = date.getTime();
       }
       var success = function(data, status) {
         var profile_callback_start_time = 0;

         if (profile_start_time) {
            var date = new Date();
            profile_callback_start_time = date.getTime();
         }

         if (typeof($overlay_div) == 'object')
             $overlay_div.hide();

         callback(data);

         if (profile_start_time) {
            var date = new Date();
            var profile_end_time = date.getTime();
            var time_for_load = profile_callback_start_time - profile_start_time;
            var time_for_callback = profile_end_time - profile_callback_start_time;
            var total_time = profile_end_time - profile_start_time;

            moksha.info('loading "' + path + '" took ' + total_time + 'ms. (Load time: ' + time_for_load + 'ms, Processing time: ' + time_for_callback + 'ms)');
         }
       }

       var error = function(XMLHttpRequest, status, err) {
         // TODO: provide a reload link in the overlay
         if (typeof($overlay_div) == 'object') {
             var $msg = $('.message', $overlay_div);
             moksha.error(err);

             $msg.html('Error loading the data for this page element');
         }
       }

       // show loading
       if (typeof($overlay_div) == 'object') {
           if (typeof(loading_icon) == 'undefined')
               loading_icon = '/images/spinner.gif';

           var $msg = $('.message', $overlay_div);
           // FIXME: make this globally configurable
           $msg.html('<img src="'+ loading_icon + '"></img>');

           var $parent = $overlay_div.parent();
           $overlay_div.css({'height': $parent.height(),
                             'width': $parent.width()})
           $overlay_div.show();
       }

       o = {
            'url': path,
            'data': params,
            'success': success,
            'error': error,
            'dataType': data_type
           }

       return $.ajax(o);
    },

    debug: function(msg) {
      if (typeof(console) != 'undefined' && typeof(console.log) != 'undefined' && typeof(moksha_debug) != 'undefined' && moksha_debug) {
          // TODO: make this configurable (or perhaps just overriding this
          //       method is enough

          console.log(msg);
      }
    },

    error: function(msg) {
         // TODO: Make this do something to indicate it is different from a
         //       warning or info message
         moksha.debug(msg);
    },

    warn: function(msg) {
         // TODO: Make this do something to indicate it is different from a
         //       error or info message
         moksha.debug(msg);
    },

    log: function(msg) {
         moksha.debug(msg);
    },

    info: function(msg) {
         // TODO: Make this do something to indicate it is different from a
         //       warning or error message
         moksha.debug(msg);
    },

    shallow_clone: function(obj) {
        var i;
        for (i in obj) {
            this[i] = obj[i];
        }
    },

    get_base_url: function(obj) {
        var burl = '/';

        if (typeof(moksha_base_url) != 'undefined')
            burl = moksha_base_url;

        return burl;
    },

    url: function(url, params) {
       if (typeof(params) == 'undefined')
            params = {};

       var purl = moksha.parseUri(url);

       if (!purl.protocol) {
           var burl = moksha.get_base_url();
           purl.prepend_base_url(burl);
           purl.update_query_string(params);

           moksha.csrf_rewrite_uri(purl);
       }

       return purl.toString();
    }
}

})();

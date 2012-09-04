// This file is part of Moksha.
// Copyright (C) 2008-2009  Red Hat, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var _extensions = function(){};

_extensions.prototype = {
    _extension_cache: {},
    _extension_deferred: {},
    _extension_uid_counter: 0,
    get_uid: function()
      {
          uid = this._extension_uid_counter +
            "_" + (Math.floor(Math.random() * 10000000));
          this._extension_uid_counter++;

          return uid;
      },
    grep_extensions: function(frag)
      {
        // FIXME: I would like to use namespaces and custom tags but
        //        IE makes this dificult (and JQuery doesn't fully support it
        //        so use div with a class instead
        var extension_points = jQuery('div.moksha_extpoint', frag);
        extension_points.each
          (
            function(i)
              {
                var ep = $(this);
                var data = ep.text();
                //remove the extension point
                ep.replaceWith('');

                data = data.replace(/'/g, "\"");
                data = data.replace(/\n/g, "");
                data = $.secureEvalJSON(data);

                moksha.extensions.load_extensions(data);
              }
          );
      },
    load_ui: function(ui, js)
      {
        id = js.placeholder_id;
        ui = eval("new myfedora.ui." + ui + "('" + id + "')");
        ui.set_show_effect(js.show_effect);
        ui.set_hide_effect(js.hide_effect);
      },
    run_extensions: function (js, data)
      {
        if (!js)
          {
            return;
          }

        var obj_list = js;

        if (data.hide_parent)
          jQuery("#" + data.hide_parent).hide();

        var append_div = jQuery("#" + data.placeholder_id);

        for(var i = 0; i < obj_list.length; i++) {
          var block_element;
          if (append_div.is('ul') ||
              append_div.is('ol')) {
            block_element = jQuery('<li/>')
          } else {
            block_element = jQuery('<div/>')
          }
          //clone our data and generate our uid so we are unique
          var d = new moksha.shallow_clone(data);
          d.uid = "extension_" + this.get_uid();

          //create a place to put this extension that they can call their own
          var div = block_element.attr("id", d.uid);

          append_div.append(div);
          var overlay = jQuery('<div><span class="message"></span></div>');
          div.append(overlay);
          d.overlay = overlay;

          //run the script and parse in the results
          try {
            var result = obj_list[i].run(d);
            if (!result) {
                result = '';
            }
          } catch (error) {
            moksha.error('Extension Point Error (' + data.type + '): ' + error.toString());
            continue;
          }

          div.append(result);

          if (!data.ui) {
            if (data.show_effect) {
              eval("append_div." + data.show_effect);
            } else {
              div.show();
            }
          }

        }

      },

    load_extensions: function (data)
      {
        var ext_code = this._extension_cache[data.type];
        var ext_deferred = this._extension_deferred[data.type];

        /* prep ui if this extention point is a ui element */
        var use_ui = data.ui;

        if (use_ui)
          {
            this.load_ui(use_ui, data);
          }

        /* run the code if it is in our cache */
        if (ext_code)
          {
            this.run_extensions(ext_code, data);
            return;
          }
        else if (ext_deferred)
          {
            this._extension_deferred[data.type].push(data);
            return;
          }

        this._extension_deferred[data.type] = new Array();
        this._extension_deferred[data.type].push(data);

        // we trust the server so we can just script inject the js
        // it should be a list of objects with a run method and code to execute
        // the modules
        var js_script_tag = jQuery('<script />');

        var attrs ={'type':'text/javascript',
                    'src': moksha.url('/moksha_extension_point', {'exttype': data.type})
                   };

        js_script_tag.attr(attrs);

        jQuery('head:first').append(js_script_tag);
      }
};

moksha.extensions = new _extensions();

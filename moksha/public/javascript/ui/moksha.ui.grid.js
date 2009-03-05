(function($) {
  $.widget("ui.mokshagrid",{
    /* methods */

    init: function() {
      var self = this;
      var o = self.options;

      self.$visible_rows = [];

      // add placeholder for row appends
      self.$rowplaceholder = jQuery('<span />').addClass('moksha_rowplaceholder');
      self.$rowplaceholder.hide();


      if (!self.element.is('table')) {
          var t = self._generate_table();

          self.element.append(t);
      } else {
          self._setup_template();
      }
    },

    destroy: function() {
        this.$headers.unbind('.mokshagrid');
        this.element.unbind('.mokshagrid');
    },

    clear: function() {
       var self = this;
       var rows = self.$visible_rows;
       for (i in rows)
           rows[i].replaceWith('');

       self.$visible_rows = [];
    },

    insert_row: function(i, row_data) {
        var self = this;
        var o = self.options
        var rows = self.$visible_rows;
        var row_count = self.visible_row_count();

        // store the widget for this element
        jQuery.data(self.element, 'mokshagrid', self);

        // do nothing if we are asked to insert passed
        // the number of rows being displayed
        if (i >= o.rows_per_page || (i == -1  && row_count >= o.rows_per_page))
            return;

        var new_row = jQuery(o.row_template.apply(row_data));

        if (i == -1 || row_count == i) {
            // append to the end of the tracking array and the table dom
            rows.push(new_row);
            self.$rowplaceholder.before(new_row);
        } else {

            // insert before i element in the tracking array and table dom
            rows[i].before(new_row);
            rows.splice(i, 0, new_row);

            // if there is one too many rows remove the last one
            if (row_count == o.rows_per_page)
                self.remove_row(o.rows_per_page);
        }

        new_row.show();
    },

    append_row: function(row_data) {
        var self = this;
        self.insert_row(-1, row_data);
    },

    remove_row: function(i) {
        var self = this;
        var rows = self.$visible_rows;
        rows[i].replaceWith('');
        rows.splice(i,1);
    },

    get_json:  function(path, args, callback) {
        //TODO: implement a json loading method
        //      which starts and stops a loading
        //      throbber
        var self = this;

        self.element.find('tbody').fadeOut('slow');
        var xmlrequest = jQuery.getJSON(path, args, function (json) {
            callback(json);
            self.element.find('tbody').fadeIn('slow');

        });

    },

    connector_query_model: function(connector, path, callback) {
        path = '/moksha_connector/' + connector + '/query_model/' + path;
        this.get_json(path, {}, callback);
    },

    connector_query: function(connector, path, dispatch_data, callback) {
        path = '/moksha_connector/' + connector + '/query/' + path;
        if (dispatch_data)
            path = path + '/' + $.toJSON(dispatch_data);

        this.get_json(path, {}, callback);
    },

    request_data_refresh: function(event) {
        // TODO: allow an optional rows_requested parameter
        var self = this;
        var o = self.options;

        // figure out which row to start with
        var rpp = o.rows_per_page;
        var start_row = (o.page_num - 1) * rpp;

        // setup the search criteria
        var search_criteria = {
            filters: o.filters,
            start_row: start_row,
            rows_requested: rpp,
            sort_key: o.sort_key,
            sort_order: o.sort_order,
        }

        // TODO: Only trigger refresh signal if we have a cache miss
        self.refresh_data(event, search_criteria);
    },

    refresh_data: function(event, search_criteria) {
        var self = this;
        var o = self.options;

        if (!o.resource || !o.resource_path)
            return;

        var results = function(json) {
            self.clear();
            for (var i in json.rows) {
                self.append_row(json.rows[i]);
            }
        }

        var filters = search_criteria.filters

        var dispatch_data = {offset: search_criteria.start_row,
                             num_rows: search_criteria.rows_requested,
                             filters: filters
                             }

        if (search_criteria.sort_key) {
            dispatch_data["sort_col"] = search_criteria.sort_key;
            dispatch_data["sort_order"] = search_criteria.sort_order;
        }

        self.connector_query(
                      o.resource,
                      o.resource_path,
                      dispatch_data,
                      results);
    },

    /* Signals */
    ready: function(event, user_data) {

    },

    /* Getter/Setters */

    visible_row_count: function() {
        var self = this;
        return self.$visible_rows.length;
    },

    /* Private */
    _setup_template: function() {
      var self = this;
      var o = self.options;

      var rowtemplate = jQuery('.rowtemplate', self.element);
      rowtemplate.removeClass('rowtemplate')
      if (rowtemplate.length)
          rowtemplate.after(self.$rowplaceholder);

      // hack to get the full html of the template including the root tag
      // this also removes the template from the document
      var container_div = jQuery('<div />');
      var html = unescape(container_div.append(rowtemplate).html());

      o.row_template = jQuery.template(html, {regx:'moksha'}).compile();

      self.$headers =  $('th:has(a[href])', this.element);
      //self.$headers = this.$ths.map(function() { return $('a', this)[0]; });
      self.$headers.unbind(o.event + '.mokshagrid').bind(o.event + '.mokshagrid', function(event) {
        var ckey = o.sort_key;
        var corder = o.sort_order;
        var key = event.originalTarget.hash.substr(1);

        if (key == ckey) {
            if (corder == -1) {
                corder = 1;
            } else {
                corder = -1;
            }
        } else {
            corder = 'decending';
        }

        self.options['sort_key'] = key;
        self.options['sort_order'] = corder;

        self.request_data_refresh();

        return false;
      })

      self.request_data_refresh();
    },

    _generate_table: function() {
        var self = this;
        var t = $('<table />');
        var o = self.options;
        // get the model if there is a resource and path
        if (!o.resource || !o.resource_path)
            return t;

        var results = function(json) {
            o.sort_key = json.default_sort_col;
            o.sort_order = json.default_sort_order;

            var headers = $('<thead />');
            var header_tr = $('<tr />');
            headers.append(header_tr);
            t.append(headers);

            var template =  $('<tbody />').addClass("rowtemplate");
            var template_tr = $('<tr />');
            template.append(template_tr);
            t.append(template);

            for (var c in json.columns) {
                var c_data = json.columns[c];
                if (!c_data.default_visible)
                    continue;

                if (c_data.can_sort) {
                    var a = $('<a />').attr('href', '#' + c).text(c);
                    var th = $('<th />').append(a);
                    header_tr.append(th);
                } else {
                    var td = $('<th />').text(c);
                    header_tr.append(td);
                }

                template_tr.append('<td>@{' + c + '}</td>');
            }

            self._setup_template();
        }

        self.connector_query_model(
                      o.resource,
                      o.resource_path,
                      results);

        return t;
    }
  })

  $.extend($.ui.mokshagrid, {
          version: '@VERSION',
          getters: 'visible_row_count',
          defaults: {
                 event: 'click',
                 rows_per_page: 10,
                 page_num: 1,
                 total_rows: 0,
                 filters: {},
                 unique_key: undefined,
                 sort_key: undefined,
                 sort_order: -1,
                 row_template: null,
                 resource: null,
                 resource_path: null,
                 loading_throbber: ["Loading",    // list of img urls or text
                                    "Loading.",
                                    "Loading..",
                                    "Loading..."]
          }
  });

$.extend( $.template.regx , {
             moksha:/\@\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g
           }
);

$.extend( $.template.helpers , {
            index: function(v, i) {
                       var result;

                       try {
                           result = v[i];
                       } catch(err) {
                           result = '&nbsp;';
                       }
                       return result;
                   }
          }
);


})(jQuery);
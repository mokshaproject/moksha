// This file is part of Moksha.
// Copyright (C) 2008-2009  Red Hat, Inc.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

(function($) {
  $.widget("ui.mokshagrid",{
    /* methods */

    _init: function() {
      var self = this;
      var o = self.options;

      if (typeof(o.filters != 'object')) {
          try {
            self.options.filters = $.secureEvalJSON(o.filters);
          } catch(e) {
            self.options.filters = {};
            moksha.error(e);
          }
      }

      // add placeholder for row appends
      self.$rowplaceholder = jQuery('<span />').addClass('moksha_rowplaceholder');
      self.$rowplaceholder.hide();

      if (!self.element.is('table')) {
          var t = self._generate_table();

          self.element.append(t);
      } else {
          self._setup_template();
      }

      self.clear();
    },

    _destroy: function() {
        this.$headers.unbind('.mokshagrid');
        this.element.unbind('.mokshagrid');
    },

    clear: function() {
       var self = this;
       var o = self.options;
       var $ph = self.$rowplaceholder;

       /*
       var $rows = $('.' + o.rowClass, $ph.parent());

       for (j=0; j < $rows.length; j++) {
           var $blank = $(self._blank_row).addClass(o.rowClass + '_' + j.toString());
           $($rows[j]).replaceWith($blank);
       }

       for (i=j; i<o.rows_per_page; i++) {
           var $blank = $(self._blank_row).addClass(o.rowClass + '_' + i.toString());
           $ph.before($blank);
       }*/

       $('.' + o.rowClass, self.element).replaceWith('');
    },

    insert_row: function(i, row_data) {
        var self = this;
        var o = self.options
        var row_count = self.visible_row_count();

        // store the widget for this element
        jQuery.data(self.element, 'mokshagrid', self);

        // do nothing if we are asked to insert passed
        // the number of rows being displayed
        if (i >= o.rows_per_page || (i == -1  && row_count >= o.rows_per_page))
            return;

        var $new_row = jQuery(o.row_template.apply(row_data));
        var $ph = self.$rowplaceholder;
        if (i == -1 || row_count == i) {
            var row_class = o.rowClass + '_' + row_count.toString();
            $ph.parent().append($new_row);
            $new_row.addClass(row_class).addClass(o.rowClass);
        } else {
            // insert before i element and update all row numbers
            // if it is a blank row, replace the row
            var row_class = o.rowClass + '_' + i.toString();
            var $row = $('.' + row_class, $ph.parent());
            $new_row.addClass(row_class).add_class(o.rowClass);

            if($row.hasClass(o.blankRowClass)) {
              $row.replaceWith(new_row);
            } else {
              var $current_rows = $(o.rowClass, $ph.parent());
              for (j = i; j < $current_rows.length; j++) {
                  var k = j + 1;
                  var old_class = '.' + o.rowClass + '_' + j.toString();
                  var new_class = '.' + o.rowClass + '_' + k.toString();
                  $current_rows[j].removeClass(old_class);
                  $current_rows[j].addClass(new_class);

              }

              $row.before($new_row);

              if (row_count == o.rows_per_page)
                  self.remove_row(o.rows_per_page);
            }
        }

        $new_row.show();

        // run any included extension points
        if (moksha.extensions)
            moksha.extensions.grep_extensions($new_row);
    },

    append_row: function(row_data) {
        var self = this;
        self.insert_row(-1, row_data);
    },

    remove_row: function(i) {
        var self = this;
        var o = self.options;
        var $ph = self.$rowplaceholder;
        var $rows = $(row_class, $ph.parent());
        $rows[i].replaceWith('');

        //FIXME: We need to relabel rows if this is not the
        //       end of the rows
    },

    connector_query_model: function(connector, path, callback) {
        path = '/query_model/' + path;
        moksha.connector_load(connector, path, {}, callback, this.$overlay_div);
    },

    connector_query: function(connector, path, dispatch_data, callback) {
        path = '/query/' + path;
        if (dispatch_data)
            path = path + '/' + $.toJSON(dispatch_data);

        moksha.connector_load(connector, path, {}, callback, this.$overlay_div);
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
            rows_per_page: rpp,
            sort_key: o.sort_key,
            sort_order: o.sort_order,
        }

        // TODO: Only trigger refresh signal if we have a cache miss
        self.refresh_data(event, search_criteria);
    },

    goto_page: function(page) {
        this.options.page_num = page;
        this.request_data_refresh();
    },

    goto_alpha_page: function(prefix) {
        if (typeof(prefix) == 'undefined')
            prefix = '';

        if (typeof(this.options.filters) != 'object')
            this.options.filters = {}

        this.options.filters.prefix = prefix;
        this.options.page_num = 1;

        this.request_data_refresh();
    },

    request_update: function(search_criteria) {
        var self = this;

        var sc = search_criteria;

        if (typeof(sc.rows_per_page) != 'undefined')
            self.options.rows_per_page = sc.rows_per_page;

        if (typeof(sc.page_num) != 'undefined')
            self.options.page_num = sc.page_num;

        if (typeof(sc.filters) != 'undefined')
            self.options.filters = sc.filters;

        if (typeof(sc.sort_key) != 'undefined')
            self.options.sort_key = sc.sort_key;

        if (typeof(sc.sort_order) != 'undefined')
            self.options.sort_order = sc.sort_order;

        self.request_data_refresh();
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

            var tr = json.total_rows;
            var vr = self.visible_row_count();
            var sr = json.start_row;
            var rpp = json.rows_per_page;

            var msg = '';
            var pager = '';

            var show_range = vr.toString();
            // show an actual range if we are not starting from 0
            if (sr > 0)
                show_range = sr.toString() + '-' + (sr + vr).toString();


            msg = 'Viewing ' + show_range + ' of ' + tr.toString();
            msg += ' items.';

            $('.message', self.$pager_bottom_placeholder).html(msg);

            var pager;
            if (o.more_link)
                pager = self._generate_more_link(o.more_link,
                                                 search_criteria.filters);
            else
                pager = self._generate_numerical_pager(tr, sr, rpp);

            $('.pager', self.$pager_bottom_placeholder).html(pager);
            self.$pager_bottom_placeholder.show();

            if (o.alphaPager) {
                pager = self._generate_alpha_pager();
                $('.pager', self.$pager_top_placeholder).html(pager);
                self.$pager_top_placeholder.show();
            }
        }

        var dispatch_data = {}

        var filters = search_criteria.filters
        if (typeof(filters) != 'undefined')
            dispatch_data['filters'] = filters

        var rows_per_page = search_criteria.rows_per_page
        if (typeof(rows_per_page) != 'undefined')
            dispatch_data['rows_per_page'] = rows_per_page

        var start_row = search_criteria.start_row
        if (typeof(start_row) != 'undefined')
            dispatch_data['start_row'] = start_row

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
        var o = self.options;
        var $ph = self.$rowplaceholder;
        var $rows = $('.' + o.rowClass, $ph.parent());

        for (i=$rows.length; i > 0; i--) {
            if (!$($rows[i-1]).hasClass(o.blankRowClass))
                return i;
        }

        return 0;
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

      o.row_template = jQuery.template(html, {regx:'moksha'});

      // create a blank row by taking the template HTML and replacing
      // the data inside the td's with a non breaking space
      $_blank_row = $(html).addClass(o.blankRowClass).addClass(o.rowClass);
      var $clear_td = $('td', $_blank_row)
      $clear_td.html('&nbsp;');
      self._blank_row = $('<div />').append($_blank_row).html();

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

      var $overlay = $('.overlay', self.element)
      if ($overlay.length == 0) {
          $overlay = $('<div />').addClass('overlay')
          $overlay.css({'opacity': .75,
                        'z-index': 99,
                        'background-color': 'white',
                        'position': 'absolute',
                       }
                      )

          $overlay.append($('<div />').addClass('message'));
          $overlay.hide();

      }

      self.element.parent().prepend($overlay);
      self.$overlay_div = $overlay;

      var $pager_top_placeholder = $('<div></div>').addClass(o.pagerTopClass).hide();
      $pager_top_placeholder.append($("<div></div>").addClass('pager'));
      $pager_top_placeholder.insertBefore(self.element);
      self.$pager_top_placeholder = $pager_top_placeholder;

      var $pager_bottom_placeholder = $('<div></div>').addClass(o.pagerBottomClass).hide();
      $pager_bottom_placeholder.append($("<div />").addClass('message'));
      $pager_bottom_placeholder.append($("<div></div>").addClass('pager'));
      $pager_bottom_placeholder.insertAfter(self.element);
      self.$pager_bottom_placeholder = $pager_bottom_placeholder;

      self.request_data_refresh();
    },

    _generate_more_link: function (more_link, filters) {
        var go = moksha.csrf_rewrite_url(more_link, filters);
        var pager = $('<a>View more ></a>').attr('href',
                                     'javascript:moksha.goto("' + go + '")');

        return pager;
    },

    _generate_alpha_pager: function () {
        var self = this;
        var o = self.options;
        var curr_alpha = o.filters.prefix;
        if (typeof(curr_alpha) == 'undefined')
            current_alpha = '';

        var pager = $('<ul />');
        var goto_page = function() {
                    var page_jump = $(this).data('alpha_page.moksha_grid');
                    self.goto_alpha_page(page_jump);
                }

        var alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        for (i in alph) {
            var a = alph[i];

            var page = $('<li />').html(a).addClass('page-button').addClass('current-page');
            if (a!=curr_alpha) {
                page.removeClass('current-page');

                var page_link = $('<a href="javascript:void(0)"></a>').html(a);
                page_link.data('alpha_page.moksha_grid', a);
                page_link.click(goto_page);

                page.html(page_link);
            }

            pager.append(page);
        }

        var page = $('<li>All</li>').addClass('page-button').addClass('current-button');
        if (curr_alpha != '') {
           var page_link = $('<a href="javascript:void(0)"></a>').html('All');

           page_link.data('alpha_page.moksha_grid', '');
           page_link.click(goto_page);

           page.html(page_link);
        }

        pager.append(page);

        return pager;
    },

    _generate_numerical_pager: function (total_rows, start_row, rows_per_page) {
        var self = this;
        var o = self.options;
        var total_pages = parseInt(total_rows / rows_per_page);
        if (total_rows != total_pages * rows_per_page)
            total_pages += 1;

        var curr_page = parseInt((start_row + 0.5) / rows_per_page) + 1;

        var next_page = curr_page + 1;

        var pager = $('<ul />');
        var goto_page = function() {
                    var page_jump = $(this).data('page.moksha_grid');
                    self.goto_page(page_jump);
                }

        var show_prev = parseInt((o.pagerPageLimit + 0.5) / 2) + 1;
        var show_next = o.pagerPageLimit - show_prev;
        var num_next_left = total_pages - curr_page;
        if (num_next_left < show_next)
            show_prev += (show_next - num_next_left)

        var page_list = [];
        var i, j;
        for (i = curr_page, j = 0; i > 0 && j < show_prev ; i--, j++) {
            page_list.push(i);
        }

        page_list.reverse();
        if (page_list.length < show_prev)
            show_next += (show_prev - page_list.length)

        for (i = curr_page + 1, j = 0; i <= total_pages && j < show_next ; i++, j++) {
            page_list.push(i);
        }

        for (i in page_list) {
            var page_num = page_list[i];
            var page = $('<li></li>').html(page_num).addClass('page-button').addClass('current-page');
            if (page_num != curr_page) {
                page.removeClass('current-page');
                var page_link = $('<a href="javascript:void(0)"></a>').html(page_num);

                page_link.data('page.moksha_grid', page_num);
                page_link.click(goto_page);

                page.html(page_link);
            }

            pager.append(page);
        }

        var page = $("<li>Next</li>").addClass('page-button').addClass('next-page');

        if (curr_page < total_pages) {
             var page_link = $('<a href="javascript:void(0)"></a>').html('Next');

             page_link.data('page.moksha_grid', next_page);
             page_link.click(goto_page);
             page.html(page_link);
        }

        pager.append(page);

        return(pager);
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
                 blankRowClass: 'moksha-grid-blank-row',
                 rowClass: 'moksha-grid-row',
                 moreClass: 'moksha-grid-more',
                 pagerTopClass: 'moksha-grid-pager-top',
                 pagerBottomClass: 'moksha-grid-pager-bottom',
                 pagerPageLimit: 10,
                 alphaPager: false,
                 more_link: null,
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
                   },

            filter: function(v, filter_cb) {
                        return window[filter_cb](v);
                    }
          }
);


})(jQuery);

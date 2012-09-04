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

/*
 * Moksha UI Tabs
 *
 * Taken from JQuery.UI.Tabs - use this for now until we can subclass
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Tabs
 *
 * Depends:
 *  ui.core.js
 */

(function($) {

$.widget("ui.mokshatabs", $.ui.tabs, {
    options: {
        staticLoadOnClick: false,
        container_level: 0,

        // Ajax
        spinner: '<em>Loading&#8230;</em>',
        cache: false,
        idPrefix: 'ui-tabs-',
        ajaxOptions: {},
        passPathRemainder:false,

        // templates
        tabTemplate: '<li><a href="#{href}"><span>#{label}</span></a></li>'
    },
    _create: function() {
        this._findParentNav();

        // create tabs
        this._tabify(true);
    },

    _findParentNav: function() {
        var parent = this.element.parent();
        var container_level = 0;
        var nav_class = 'moksha-ui-navcontainer';

        while (parent.length && !container_level) {
            if (parent.hasClass(nav_class))
                container_level = parent.data('moksha_container_level') + 1;
            else
                parent = parent.parent()
        }

        this.options.container_level = container_level;
    },

    _stripUUID: function(id) {
        return id.split("-uuid")[0];
    },

    _generateTabLink: function(tab_path, attach_query_string) {
      o = this.options;
      var container_path = location.hash.substr(1);
      var tab_link = container_path.split('/');
      tab_link[o.container_level] = tab_path;

      tab_link = tab_link.splice(0, o.container_level + 1).join('/');
      if (attach_query_string  && location.search)
        tab_link += location.search;

      return tab_link;
    },

    _tabId: function(a) {
        var panel = $(a).attr('panel');

        return panel && panel.replace(/\s/g, '_').replace(/[^A-Za-z0-9\-_:\.]/g, '')
            || this.options.idPrefix + $.data(a);
    },

    _tabify: function(init) {
        var tab_id = this.element.attr('id') + '_tabs';
        this.list = this.element.find('ol,ul').eq(0);
        this.lis = $('#' + tab_id + ' ul li:has(>a[href])', this.element);

        this.anchors = this.lis.map(function() { return $('a', this)[0]; });
        this.panels = $([]);

        var self = this, o = this.options;

        var first_non_static_tab = -1;
        var fragmentId = /^#.+/; // Safari 2 reports '#' for an empty hash
        this.anchors.each(function(i, a) {
            var href = $(a).attr('href');

            // For dynamically created HTML that contains a hash as href IE < 8 expands
            // such href to the full page url with hash and then misinterprets tab as ajax.
            // Same consideration applies for an added tab with a fragment identifier
            // since a[href=#fragment-identifier] does unexpectedly not match.
            // Thus normalize href attribute...
            var hrefBase = href.split('#')[0], baseEl;
            if (hrefBase && (hrefBase === location.toString().split('#')[0] ||
                    (baseEl = $('base')[0]) && hrefBase === baseEl.href)) {
                href = a.hash;
                a.href = href;
            }

            // inline tab
            if (fragmentId.test(href)) {
                self.panels = self.panels.add(self._sanitizeSelector(href));
            } else if ($(a).hasClass('static_link')) {
                $.data(a, 'href.tabs', href);
                $.data(a, 'load.tabs', href);

                a.href = moksha.url(href);
            // remote tab
            } else if (href != '#') { // prevent loading the page itself if href is just "#"
                if (first_non_static_tab == -1)
                    first_non_static_tab = i;

                $.data(a, 'href.tabs', href); // required for restore on destroy
                $.data(a, 'load.tabs', href.replace(/#.*$/, '')); // mutable

                var id = self._tabId(a);

                $(a).data('dynamic_href.tabs', '#' + id);
                a.href = self._generateTabLink(self._stripUUID(id), true);

                var $panel = $('#' + id + ':first', self.element);
                if (!$panel.length) {
                    $panel = $(o.panelTemplate).attr('id', id).addClass('ui-tabs-panel ui-widget-content ui-corner-bottom')
                        .insertAfter( self.panels[i - 1] || self.list );
                    $panel.data('destroy.tabs', true);

                }
                $panel.data('moksha_container_level', o.container_level);
                $panel.addClass('moksha-ui-navcontainer');
                self.panels = self.panels.add( $panel );
            }
            // invalid tab href
            else
                o.disabled.push(i);
        });

        var $overlay = $('.overlay', self.element)
        if ($overlay.length == 0) {
            $overlay = $('<div />')
            $overlay.css({'opacity': .75,
                        'z-index': 99,
                        'background-color': 'white',
                        'position': 'absolute'
                       }
                      )

            $overlay.addClass('overlay')

            $overlay.append($('<div />').addClass('message'));
            if (typeof(self.panels[0]) != 'undefined')
                $overlay.insertBefore(self.panels[0]);
            else
                $overlay.insertAfter(self.element);

        }

        $overlay.hide();
        self.$overlay_div = $overlay;

        if (init) {

            // attach necessary classes for styling if not present
            this.element.addClass('ui-tabs ui-widget ui-widget-content ui-corner-all');
            this.list.addClass('ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all');
            this.lis.addClass('ui-state-default ui-corner-top');
            this.panels.addClass('ui-tabs-panel ui-widget-content ui-corner-bottom');

            // Selected tab
            // use "selected" option or try to retrieve:
            // 1. from fragment identifier in url
            // 2. from cookie
            // 3. from selected class attribute on <li>
            if (o.selected === undefined) {
                if (location.hash) {
                    var index = this.hashToIndex(location.hash, o.container_level);

                    if (index >= 0) {
                        o.selected = index;
                        // prevent page scroll to fragment
                        if ($.browser.msie || $.browser.opera) { // && !o.remote
                            var $toShow = $(this.anchors[index]);
                            var toShowId = $toShow.attr('id');
                                $toShow.attr('id', '');
                                setTimeout(function() {
                                    $toShow.attr('id', toShowId); // restore id
                                }, 500);
                        }
                        scrollTo(0, 0);
                    } else if (index == -1) {
                       // invalid path, redirect to /invalid_path
                       path = location.hash.substring(1);
                       location.href=moksha.url('/invalid_path', {invalid_path: path});
                    } // else we goto the first non-static tab

                }
                else if (o.cookie) {
                    var index = parseInt(self._cookie(),10);
                    if (index && self.anchors[index])
                        o.selected = index;
                }
                else if (self.lis.filter('.' + o.selectedClass).length)
                    o.selected = self.lis.index( self.lis.filter('.ui-tabs-selected')[0] );
            }
            o.selected = o.selected === null || o.selected !== undefined ? o.selected : first_non_static_tab; // first non-static tab selected by default

            // Take disabling tabs via class attribute from HTML
            // into account and update option properly.
            // A selected tab cannot become disabled.
            o.disabled = $.unique(o.disabled.concat(
                $.map(this.lis.filter('.ui-state-disabled'),
                    function(n, i) { return self.lis.index(n); } )
            )).sort();

            if ($.inArray(o.selected, o.disabled) != -1)
                o.disabled.splice($.inArray(o.selected, o.disabled), 1);

            // highlight selected tab
            this.panels.addClass('ui-tabs-hide');
            this.lis.removeClass('ui-tabs-selected ui-state-active');
            if (o.selected >= 0 && this.anchors.length) {
                this.panels.eq(o.selected - first_non_static_tab).removeClass('ui-tabs-hide');
                var l = this.lis.eq(o.selected).addClass('ui-tabs-selected ui-state-active');

                var a = $('a', l)[0];
                var title = $(a).attr('title');
                if (title)
                    moksha.update_title(title, 1);

                //var $show = $($(a).data('dynamic_href.tabs') + ':first', self.element)

                // seems to be expected behavior that the show callback is fired
                self.element.queue("tabs", function() {
                    self._trigger('show', null, self._ui(self.anchors[o.selected], self.panels[o.selected]));
                });

                this.load(o.selected)
            }

            // clean up to avoid memory leaks in certain versions of IE 6
            $(window).bind('unload', function() {
                self.lis.add(self.anchors).unbind('.tabs');
                self.lis = self.anchors = self.panels = null;
            });

        }
        // update selected after add/remove
        else {
            o.selected = this.lis.index(this.lis.filter('.ui-tabs-selected'));
        }

        // update collapsible
        this.element[o.collapsible ? 'addClass' : 'removeClass']('ui-tabs-collapsible');

        // set or update cookie after init and add/remove respectively
        if (o.cookie) {
            this._cookie(o.selected, o.cookie);
        }

        // disable tabs
        for (var i = 0, li; (li = this.lis[i]); i++) {
            $(li)[$.inArray(i, o.disabled) != -1 &&
                !$(li).hasClass('ui-tabs-selected') ? 'addClass' : 'removeClass']('ui-state-disabled');
        }

        // reset cache if switching from cached to not cached
        if (o.cache === false)
            this.anchors.removeData('cache.tabs');

        // remove all handlers before, tabify may run on existing tabs after add or option change
        this.lis.add(this.anchors).unbind('.tabs');

        if (o.event != 'mouseover') {
            var addState = function(state, el) {
                if (el.is(':not(.ui-state-disabled)')) {
                    el.addClass('ui-state-' + state);
                }
            };
            var removeState = function(state, el) {
                el.removeClass('ui-state-' + state);
            };
            this.lis.bind('mouseover.tabs', function() {
                addState('hover', $(this));
            });
            this.lis.bind('mouseout.tabs', function() {
                removeState('hover', $(this));
            });
            this.anchors.bind('focus.tabs', function() {
                addState('focus', $(this).closest('li'));
            });
            this.anchors.bind('blur.tabs', function() {
                removeState('focus', $(this).closest('li'));
            });
        }

        // set up animations
        var hideFx, showFx;
        if (o.fx) {
            if ($.isArray(o.fx)) {
                hideFx = o.fx[0];
                showFx = o.fx[1];
            }
            else {
                hideFx = showFx = o.fx;
            }
        }

        // Reset certain styles left over from animation
        // and prevent IE's ClearType bug...
        function resetStyle($el, fx) {
            $el.css({ display: '' });
            if (!$.support.opacity && fx.opacity) {
                $el[0].style.removeAttribute('filter');
            }
        }

        // Show a tab...
        var showTab = showFx ?
            function(clicked, $show) {
                var title = $(clicked).attr('title');
                if (title)
                    moksha.update_title(title, 1);

                $(clicked).closest('li').addClass('ui-tabs-selected ui-state-active');
                $show.hide().removeClass('ui-tabs-hide') // avoid flicker that way
                    .animate(showFx, showFx.duration || 'normal', function() {
                        resetStyle($show, showFx);
                        self._trigger('show', null, self._ui(clicked, $show[0]));
                    });
            } :
            function(clicked, $show) {
                var title = $(clicked).attr('title');
                if (title)
                    moksha.update_title(title, 1);

                $(clicked).closest('li').addClass('ui-tabs-selected ui-state-active');
                $show.removeClass('ui-tabs-hide');
                self._trigger('show', null, self._ui(clicked, $show[0]));
            };

        // Hide a tab, $show is optional...
        var hideTab = hideFx ?
            function(clicked, $hide) {
                $hide.animate(hideFx, hideFx.duration || 'normal', function() {
                    self.lis.removeClass('ui-tabs-selected ui-state-active');
                    $hide.addClass('ui-tabs-hide');
                    resetStyle($hide, hideFx);
                    self.element.dequeue("tabs");
                });
            } :
            function(clicked, $hide, $show) {
                self.lis.removeClass('ui-tabs-selected ui-state-active');
                $hide.addClass('ui-tabs-hide');
                self.element.dequeue("tabs");
            };

         // attach tab event handler, unbind to avoid duplicates from former tabifying...
        this.anchors.bind(o.event + '.tabs', function() {
            // if we have a static link use that instead
            var isStaticLink = $(this).hasClass('static_link');
            if (isStaticLink)
                return true;

            var el = this, $li = $(this).closest('li'), $hide = self.panels.filter(':not(.ui-tabs-hide)'),
                    $show = $($(this).data('dynamic_href.tabs') + ':first', self.element);

            // If tab is already selected and not collapsible or tab disabled or
            // or is already loading or click callback returns false stop here.
            // Check if click handler returns false last so that it is not executed
            // for a disabled or loading tab!
            if (($li.hasClass('ui-tabs-selected') && !o.collapsible) ||
                $li.hasClass('ui-state-disabled') ||
                $li.hasClass('ui-state-processing') ||
                self._trigger('select', null, self._ui(this, $show[0])) === false) {
                this.blur();
                return false;
            }

            o.selected = self.anchors.index(this);

            var $el = $(this)

            // we don't get the actual href but the dynamic one
            var href = $el.data('dynamic_href.tabs');

            href = self._stripUUID(href);

            //only update the hash level we care about
            if (o.container_level != 0) {
              var hash = self._generateTabLink(href.substr(1), false);

              if (o.staticLoadOnClick) {
                  moksha.goto(hash);
                  return false;
              } else {
                  location.hash = '#' + hash;
              }
            } else {
              if (o.staticLoadOnClick) {
                  moksha.goto('/' + href.substr(1));
                  return false;
              } else {
                  location.hash = href;
              }
            }

            // if tab may be closed
            if (o.collapsible) {
                if ($li.hasClass('ui-tabs-selected')) {
                    o.selected = -1;

                    if (o.cookie) {
                        self._cookie(o.selected, o.cookie);
                    }

                    self.element.queue("tabs", function() {
                        hideTab(el, $hide);
                    }).dequeue("tabs");

                    this.blur();
                    return false;
                }
                else if (!$hide.length) {
                    if (o.cookie) {
                        self._cookie(o.selected, o.cookie);
                    }

                    self.element.queue("tabs", function() {
                        showTab(el, $show);
                    });

                    self.load(self.anchors.index(this)); // TODO make passing in node possible, see also http://dev.jqueryui.com/ticket/3171

                    this.blur();
                    return false;
                }
            }

            if (o.cookie) {
                self._cookie(o.selected, o.cookie);
            }

            // show new tab
            if ($show.length) {
                if ($hide.length) {
                    self.element.queue("tabs", function() {
                        hideTab(el, $hide);
                    });
                }
                self.element.queue("tabs", function() {
                    showTab(el, $show);
                });

                self.load(self.anchors.index(this));
            }
            else {
                throw 'jQuery UI Tabs: Mismatching fragment identifier.';
            }

            // Prevent IE from keeping other link focussed when using the back button
            // and remove dotted border from clicked link. This is controlled via CSS
            // in modern browsers; blur() removes focus from address bar in Firefox
            // which can become a usability and annoying problem with tabs('rotate').
            if ($.browser.msie) {
                this.blur();
            }

            // we've handled the event so stop it from propagating
            return false;

        });

    },
    add: function(url, label, index) {
        if (index == undefined)
            index = this.anchors.length; // append by default

        var self = this, o = this.options,
            $li = $(o.tabTemplate.replace(/#\{href\}/g, url).replace(/#\{label\}/g, label)),
            id = !url.indexOf('#') ? url.replace('#', '') : this._tabId( $('a:first-child', $li)[0] );

        $li.addClass('ui-state-default ui-corner-top').data('destroy.tabs', true);

        // try to find an existing element before creating a new one
        var $panel = $('#' + id, this.list);
        if (!$panel.length) {
            $panel = $(o.panelTemplate).attr('id', id).data('destroy.tabs', true);
        }
        $panel.addClass('ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide');
        if (index >= this.lis.length) {
            $li.appendTo(this.list);
            $panel.appendTo(this.list[0].parentNode);
        } else {
            $li.insertBefore(this.lis[index]);
            $panel.insertBefore(this.panels[index]);
        }

        o.disabled = $.map(o.disabled,
            function(n, i) { return n >= index ? ++n : n });

        this._tabify();

        if (this.anchors.length == 1) {
            $li.addClass('ui-tabs-selected ui-state-active');
            $panel.removeClass('ui-tabs-hide');
            this.element.queue("tabs", function() {
                self._trigger('show', null, self._ui(self.anchors[0], self.panels[0]));
            });
        }

        this.load(0);

        // callback
        this._trigger('add', null, this._ui(this.anchors[index], this.panels[index]));
        return this;
    },

    // get the selected tab index give a location hash
    hashToIndex: function(_hash, level) {
        var hash = _hash;
    	var offset = 0;

        //remove the has because we only care about the / delimiter
        if (hash.charAt(0) == "#")
            hash = hash.substr(1);

        hash_items = hash.split("/");
        // get the first id ignoring leading slashes
        for (var i=0; i<hash_items.length, !hash_items[i]; i++) {
            offset++;
        }

        var id_index = level + offset;
        if (id_index >= hash_items.length)
            return -2;

        var id = "#" + hash_items[level + offset];

        var remainder = level + offset + 1;
        if (this.options.passPathRemainder && hash_items.length > remainder)
            this.path_remainder = '/' + hash_items.splice(level + offset + 1).join('/');

        moksha.info('moksha.ui.tabs.js (hashToIndex): Selecting element ' + level + '(' + id + ') from hash "' + hash + '"');
        return this.idToIndex(id);
    },
    idToIndex: function(id) {
        var index = -1;
        var l = id.length;
        for(var i=0; i < this.anchors.length; i++) {
            var h = $(this.anchors[i]).data('dynamic_href.tabs');
            // static links do not count
            if (!h)
                continue;

            h = this._stripUUID(h);
            if (h == id) {
                index = i;
                break;
            }
        }

        return (index);
    },
    select: function(index) {
        if (typeof index == 'string')
            index = this.idToIndex(index);
        else if(index === null) { // usage of null is deprecated, TODO remove in next release
            index = -1;
        }

        if (index == -1 && this.options.collapsible) {
            index = this.options.selected;
        }

        this.anchors.eq(index).trigger(this.options.event + '.tabs');
        return this;
    },

    load: function(index, callback) { // callback is for internal usage only

        var self = this, o = this.options, a = this.anchors.eq(index)[0],
                bypassCache = callback == undefined || callback === false, url = $.data(a, 'load.tabs');

        callback = callback || function() {};

        this.abort();

        // not remote or from cache - just finish with callback
        if (!url || this.element.queue("tabs").length !== 0 && !bypassCache && $.data(a, 'cache.tabs')) {
            this.element.dequeue("tabs");
            callback();
            return;
        }

        // load remote from here on
        this.lis.eq(index).addClass('ui-state-processing');

        var inner = function(parent) {
            var $parent = $(parent), $inner = $parent.find('*:last');
            return $inner.length && $inner.is(':not(img)') && $inner || $parent;
        };

        if (o.spinner) {
            var span = $('span', a);
            if (span.length == 0)
                span = inner(a).wrapInner('<span></span>').find('span');

            span.data('label.tabs', span.html()).html(o.spinner);
        }

        var success_cb = function(r, s) {
                var id = $(a).data('dynamic_href.tabs')
                var $panel = $(id + ':first', self.element);
                var $stripped = moksha.filter_resources(r);

                $panel.html($stripped);
                self._cleanup();

                if (o.cache)
                    $.data(a, 'cache.tabs', true); // if loaded once do not load them again

                // callbacks
                self._trigger('load', null, self._ui(self.anchors[index], self.panels[index]));

                // This callback is required because the switch has to take
                // place after loading has completed. Call last in order to
                // fire load before show callback...
                callback();
            }

        if (this.xhr) {
            // terminate pending requests from other tabs and restore tab label
            this.xhr.abort();
            self._cleanup();
        }


        this.xhr = moksha.html_load(moksha.url(url), {}, success_cb, self.$overlay_div);
        self.element.dequeue("tabs");

        return this;
    }

});

})(jQuery);

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

$.widget("ui.mokshatabs", {

    _init: function() {
        this.options.event += '.tabs'; // namespace event

        this._findParentNav();

        // create tabs
        this.tabify(true);
    },

    _findParentNav: function() {
        var parent = this.element.parent();
        var container_level = 0;
        var nav_class = this.options.navContainerClass;

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

    setData: function(key, value) {
        if ((/^selected/).test(key))
            this.select(value);
        else {
            this.options[key] = value;
            this.tabify();
        }
    },

    length: function() {
        return this.$tabs.length;
    },

    tabId: function(a) {
        var panel = $(a).attr('panel');

        return panel && panel.replace(/\s/g, '_').replace(/[^A-Za-z0-9\-_:\.]/g, '')
            || this.options.idPrefix + $.data(a);
    },

    ui: function(tab, panel) {
        return {
            options: this.options,
            tab: tab,
            panel: panel,
            index: this.$tabs.index(tab)
        };
    },

    tabify: function(init) {

        var tab_id = this.element.attr('id') + '_tabs';
        this.$lis = $('#' + tab_id + ' ul li:has(>a[href])', this.element);

        this.$tabs = this.$lis.map(function() { return $('a', this)[0]; });

        this.$panels = $([]);

        var self = this, o = this.options;

        var first_non_static_tab = -1;
        this.$tabs.each(function(i, a) {
            // inline tab
            if (a.hash && a.hash.replace('#', '')) { // Safari 2 reports '#' for an empty hash
                self.$panels = self.$panels.add(a.hash);
                if (first_non_static_tab == -1)
                    first_non_static_tab = i;
            // static link
            } else if ($(a).hasClass('static_link') || o.staticLinkOnClick) {
                $.data(a, 'href.tabs', href);
                $.data(a, 'load.tabs', href);
            // remote tab
            } else if ($(a).attr('href') != '#') { // prevent loading the page itself if href is just "#"
                if (first_non_static_tab == -1)
                    first_non_static_tab = i;

                var href = $(a).attr('href')
                $.data(a, 'href.tabs', href); // required for restore on destroy
                $.data(a, 'load.tabs', href); // mutable
                var id = self.tabId(a);

                $(a).data('dynamic_href.tabs', '#' + id);
                a.href = moksha.url(self._generateTabLink(self._stripUUID(id), true));

                var $panel = $('#' + id + ':first', self.element);
                if (!$panel.length) {
                    $panel = $(o.panelTemplate).attr('id', id).addClass(o.panelClass)
                        .insertAfter( self.$panels[i - 1] || self.element );
                    $panel.data('destroy.tabs', true);

                }
                $panel.data('moksha_container_level', o.container_level);
                $panel.addClass(o.navContainerClass);

                self.$panels = self.$panels.add( $panel );
            }
            // invalid tab href
            else
                o.disabled.push(i + 1);
        });

        var $overlay = $('.overlay', self.element)
        if ($overlay.length == 0) {
            $overlay = $('<div />')
            $overlay.css({'opacity': .75,
                        'z-index': 99,
                        'background-color': 'white',
                        'position': 'absolute',
                       }
                      )

            $overlay.addClass('overlay')

            $overlay.append($('<div />').addClass('message'));
            if (typeof(self.$panels[0]) != 'undefined')
                $overlay.insertBefore(self.$panels[0]);
            else
                $overlay.insertAfter(self.element);

        }

        $overlay.hide();
        self.$overlay_div = $overlay;

        if (init) {

            // attach necessary classes for styling if not present
            this.element.addClass(o.navClass);
            if (jQuery(this.element).effectivedirection() == 'rtl') {
                this.element.addClass(o.navClass_rtl);
            }
            this.$panels.each(function() {
                var $this = $(this);
                $this.addClass(o.panelClass);
            });

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
                            var $toShow = $(this.$tabs[index]);
                            var toShowId = $toShow.attr('id');
                                $toShow.attr('id', '');
                                setTimeout(function() {
                                    $toShow.attr('id', toShowId); // restore id
                                }, 500);
                        }
                        scrollTo(0, 0);
                    }

                }
                else if (o.cookie) {
                    var index = parseInt($.cookie('ui-tabs' + $.data(self.element)),10);
                    if (index && self.$tabs[index])
                        o.selected = index;
                }
                else if (self.$lis.filter('.' + o.selectedClass).length)
                    o.selected = self.$lis.index( self.$lis.filter('.' + o.selectedClass)[0] );
            }
            o.selected = o.selected === null || o.selected !== undefined ? o.selected : first_non_static_tab; // first non-static tab selected by default

            // Take disabling tabs via class attribute from HTML
            // into account and update option properly.
            // A selected tab cannot become disabled.
            o.disabled = $.unique(o.disabled.concat(
                $.map(this.$lis.filter('.' + o.disabledClass),
                    function(n, i) { return self.$lis.index(n); } )
            )).sort();
            if ($.inArray(o.selected, o.disabled) != -1)
                o.disabled.splice($.inArray(o.selected, o.disabled), 1);

            // highlight selected tab
            this.$panels.addClass(o.hideClass);
            this.$lis.removeClass(o.selectedClass);
            if (o.selected !== null) {

                var l = this.$lis.eq(o.selected).addClass(o.selectedClass);
                var a = $('a', l)[0];
                var $show = $($(a).data('dynamic_href.tabs') + ':first', self.element)
                $show.show().removeClass(o.hideClass); // use show and remove class to show in any case no matter how it has been hidden before

                // seems to be expected behavior that the show callback is fired
                var onShow = function() {
                    $(self.element).triggerHandler('tabsshow',
                        [self.fakeEvent('tabsshow'), self.ui(self.$tabs[o.selected], self.$panels[o.selected])], o.show);
                };

                // load if remote tab
                if ($.data(this.$tabs[o.selected], 'load.tabs')) {
                    this.load(o.selected, onShow);
                // just trigger show event
                } else
                    onShow();

            }

            // clean up to avoid memory leaks in certain versions of IE 6
            $(window).bind('unload', function() {
                self.$tabs.unbind('.tabs');
                self.$lis = self.$tabs = self.$panels = null;
            });

        }

        // disable tabs
        for (var i = 0, li; li = this.$lis[i]; i++)
            $(li)[$.inArray(i, o.disabled) != -1 && !$(li).hasClass(o.selectedClass) ? 'addClass' : 'removeClass'](o.disabledClass);

        // reset cache if switching from cached to not cached
        if (o.cache === false)
            this.$tabs.removeData('cache.tabs');

        // set up animations
        var hideFx, showFx, baseFx = { 'min-width': 0, duration: 1 }, baseDuration = 'normal';
        if (o.fx && o.fx.constructor == Array)
            hideFx = o.fx[0] || baseFx, showFx = o.fx[1] || baseFx;
        else
            hideFx = showFx = o.fx || baseFx;

        // reset some styles to maintain print style sheets etc.
        var resetCSS = { display: '', overflow: '', height: '' };
        if (!$.browser.msie) // not in IE to prevent ClearType font issue
            resetCSS.opacity = '';

        // Hide a tab, animation prevents browser scrolling to fragment,
        // $show is optional.
        function hideTab(clicked, $hide, $show) {
            $hide.animate(hideFx, hideFx.duration || baseDuration, function() { //
                $hide.addClass(o.hideClass).css(resetCSS); // maintain flexible height and accessibility in print etc.
                if ($.browser.msie && hideFx.opacity)
                    $hide[0].style.filter = '';
                if ($show)
                    showTab(clicked, $show, $hide);
            });
        }

        // Show a tab, animation prevents browser scrolling to fragment,
        // $hide is optional.
        function showTab(clicked, $show, $hide) {
            if (showFx === baseFx)
                $show.css('display', 'block'); // prevent occasionally occuring flicker in Firefox cause by gap between showing and hiding the tab panels
            $show.animate(showFx, showFx.duration || baseDuration, function() {
                $show.removeClass(o.hideClass).css(resetCSS); // maintain flexible height and accessibility in print etc.
                if ($.browser.msie && showFx.opacity)
                    $show[0].style.filter = '';

                // callback
                $(self.element).triggerHandler('tabsshow',
                    [self.fakeEvent('tabsshow'), self.ui(clicked, $show[0])], o.show);

            });
        }

        // switch a tab
        function switchTab(clicked, $li, $hide, $show) {
            /*if (o.bookmarkable && trueClick) { // add to history only if true click occured, not a triggered click
                $.ajaxHistory.update(clicked.hash);
            }*/

            self.$lis.removeClass(o.selectedClass);
            $li.addClass(o.selectedClass);
            hideTab(clicked, $hide, $show);
        }

        // attach tab event handler, unbind to avoid duplicates from former tabifying...
        this.$tabs.unbind('.tabs').bind(o.event, function() {

            //var trueClick = e.clientX; // add to history only if true click occured, not a triggered click
            var $li = $(this).parents('li:eq(0)'),
                $hide = self.$panels.filter(':visible'),
                $show = $($(this).data('dynamic_href.tabs') + ':first', self.element),
                isStaticLink = $(this).hasClass('static_link');

            // If tab disabled or
            // or is already loading or click callback returns false stop here.
            // Check if click handler returns false last so that it is not executed
            // for a disabled or loading tab!
            if ($li.hasClass(o.disabledClass)
                || $(this).hasClass(o.loadingClass)
                || $(self.element).triggerHandler('tabsselect', [self.fakeEvent('tabsselect'), self.ui(this, $show[0])], o.select) === false
                ) {
                this.blur();
                return false;
            }

            self.options.selected = self.$tabs.index(this);

            var $el = $(this)

            // we don't get the actual href but the dynamic one
            var href = $el.data('dynamic_href.tabs');

            href = self._stripUUID(href);

             if (isStaticLink) {
                  moksha.goto(href);
                  return false;
             }

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
                  moksha.goto(href.substr(1));
                  return false;
              } else {
                  location.hash = href;
              }
            }

            // if tab may be closed
            if (o.unselect) {
                if ($li.hasClass(o.selectedClass)) {
                    self.options.selected = null;
                    $li.removeClass(o.selectedClass);
                    self.$panels.stop();
                    hideTab(this, $hide);
                    this.blur();
                    return false;
                } else if (!$hide.length) {
                    self.$panels.stop();
                    var a = this;
                    self.load(self.$tabs.index(this), function() {
                        $li.addClass(o.selectedClass).addClass(o.unselectClass);
                        showTab(a, $show);
                    });
                    this.blur();
                    return false;
                }
            }

            if (o.cookie)
                $.cookie('ui-tabs' + $.data(self.element), self.options.selected, o.cookie);

            // stop possibly running animations
            self.$panels.stop();

            // show new tab
            if ($show.length) {

                // prevent scrollbar scrolling to 0 and than back in IE7, happens only if bookmarking/history is enabled
                /*if ($.browser.msie && o.bookmarkable) {
                    var showId = this.hash.replace('#', '');
                    $show.attr('id', '');
                    setTimeout(function() {
                        $show.attr('id', showId); // restore id
                    }, 0);
                }*/

                var a = this;
                self.load(self.$tabs.index(this), $hide.length ?
                    function() {
                        switchTab(a, $li, $hide, $show);
                    } :
                    function() {
                        $li.addClass(o.selectedClass);
                        showTab(a, $show);
                    }
                );

                // Set scrollbar to saved position - need to use timeout with 0 to prevent browser scroll to target of hash
                /*var scrollX = window.pageXOffset || document.documentElement && document.documentElement.scrollLeft || document.body.scrollLeft || 0;
                var scrollY = window.pageYOffset || document.documentElement && document.documentElement.scrollTop || document.body.scrollTop || 0;
                setTimeout(function() {
                    scrollTo(scrollX, scrollY);
                }, 0);*/

            } else
                throw 'jQuery UI Tabs: Mismatching fragment identifier.';

            // Prevent IE from keeping other link focussed when using the back button
            // and remove dotted border from clicked link. This is controlled in modern
            // browsers via CSS, also blur removes focus from address bar in Firefox
            // which can become a usability and annoying problem with tabsRotate.
            if ($.browser.msie)
                this.blur();

            //return o.bookmarkable && !!trueClick; // convert trueClick == undefined to Boolean required in IE
            return false;
        });

        // disable click if event is configured to something else
        if (!(/^click/).test(o.event))
            this.$tabs.bind('click.tabs', function() { return false; });

    },
    add: function(url, label, index) {
        if (index == undefined)
            index = this.$tabs.length; // append by default

        var o = this.options;
        var $li = $(o.tabTemplate.replace(/#\{href\}/g, url).replace(/#\{label\}/g, label));
        $li.data('destroy.tabs', true);

        var id = url.indexOf('#') == 0 ? url.replace('#', '') : this.tabId( $('a:first-child', $li)[0] );

        // try to find an existing element before creating a new one
        var $panel = $('#' + id, this.element);
        if (!$panel.length) {
            $panel = $(o.panelTemplate).attr('id', id)
                .addClass(o.hideClass)
                .data('destroy.tabs', true);
        }
        $panel.addClass(o.panelClass);
        if (index >= this.$lis.length) {
            $li.appendTo(this.element);
            $panel.appendTo(this.element[0].parentNode);
        } else {
            $li.insertBefore(this.$lis[index]);
            $panel.insertBefore(this.$panels[index]);
        }

        o.disabled = $.map(o.disabled,
            function(n, i) { return n >= index ? ++n : n });

        this.tabify();

        if (this.$tabs.length == 1) {
            $li.addClass(o.selectedClass);
            $panel.removeClass(o.hideClass);
            var href = $.data(this.$tabs[0], 'load.tabs');
            if (href)
                this.load(index, href);
        }

        // callback
        this.element.triggerHandler('tabsadd',
            [this.fakeEvent('tabsadd'), this.ui(this.$tabs[index], this.$panels[index])], o.add
        );
    },
    remove: function(index) {
        var o = this.options, $li = this.$lis.eq(index).remove(),
            $panel = this.$panels.eq(index).remove();

        // If selected tab was removed focus tab to the right or
        // in case the last tab was removed the tab to the left.
        if ($li.hasClass(o.selectedClass) && this.$tabs.length > 1)
            this.select(index + (index + 1 < this.$tabs.length ? 1 : -1));

        o.disabled = $.map($.grep(o.disabled, function(n, i) { return n != index; }),
            function(n, i) { return n >= index ? --n : n });

        this.tabify();

        // callback
        this.element.triggerHandler('tabsremove',
            [this.fakeEvent('tabsremove'), this.ui($li.find('a')[0], $panel[0])], o.remove
        );
    },
    enable: function(index) {
        var o = this.options;
        if ($.inArray(index, o.disabled) == -1)
            return;

        var $li = this.$lis.eq(index).removeClass(o.disabledClass);
        if ($.browser.safari) { // fix disappearing tab (that used opacity indicating disabling) after enabling in Safari 2...
            $li.css('display', 'inline-block');
            setTimeout(function() {
                $li.css('display', 'block');
            }, 0);
        }

        o.disabled = $.grep(o.disabled, function(n, i) { return n != index; });

        // callback
        this.element.triggerHandler('tabsenable',
            [this.fakeEvent('tabsenable'), this.ui(this.$tabs[index], this.$panels[index])], o.enable
        );

    },
    disable: function(index) {
        var self = this, o = this.options;
        if (index != o.selected) { // cannot disable already selected tab
            this.$lis.eq(index).addClass(o.disabledClass);

            o.disabled.push(index);
            o.disabled.sort();

            // callback
            this.element.triggerHandler('tabsdisable',
                [this.fakeEvent('tabsdisable'), this.ui(this.$tabs[index], this.$panels[index])], o.disable
            );
        }
    },

    // get the selected tab index give a location hash
    hashToIndex: function(hash, level) {
        var hash = location.hash;
        var offset = 0;

        //remove the has because we only care about the / delimiter
        if (hash[0] == "#")
            hash = hash.substr(1);

        hash = hash.split("/");
        // get the first id ignoring leading slashes
        for (var i=0; i<hash.length, !hash[i]; i++) {
            offset++;
        }

        var id_index = level + offset;
        if (id_index >= hash.length)
            return -1;

        var id = "#" + hash[level + offset];

        var remainder = level + offset + 1;
        if (this.options.passPathRemainder && hash.length > remainder)
            this.path_remainder = '/' + hash.splice(level + offset + 1).join('/');

        moksha.info('moksha.ui.tabs.js (hashToIndex): Selecting element ' + level + '(' + id + ') from hash "' + hash + '"');
        return this.idToIndex(id);
    },
    idToIndex: function(id) {
        var index = -1;
        var l = id.length;
        for(var i=0; i < this.$tabs.length; i++) {
            var h = $(this.$tabs[i]).data('dynamic_href.tabs');
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

        this.$tabs.eq(index).trigger(this.options.event);
    },
    load: function(index, callback) { // callback is for internal usage only

        var self = this, o = this.options, $a = this.$tabs.eq(index), a = $a[0],
                bypassCache = callback == undefined || callback === false, url = $a.data('load.tabs');

        callback = callback || function() {};

        // no remote or from cache - just finish with callback
        if (!url || !bypassCache && $.data(a, 'cache.tabs')) {
            callback();
            return;
        }

        // load remote from here on

        var inner = function(parent) {
            var $parent = $(parent), $inner = $parent.find('*:last');
            return $inner.length && $inner.is(':not(img)') && $inner || $parent;
        };
        var cleanup = function() {
            self.$tabs.filter('.' + o.loadingClass).removeClass(o.loadingClass)
                        .each(function() {
                            if (o.spinner)
                                inner(this).parent().html(inner(this).data('label.tabs'));
                        });
            self.xhr = null;
        };

        if (o.spinner) {
            var label = inner(a).html();
            inner(a).wrapInner('<em></em>')
                .find('em').data('label.tabs', label).html(o.spinner);
        }

        var success_cb = function(r, s) {
                var id = $(a).data('dynamic_href.tabs')
                var $panel = $(id + ':first', self.element);
                var $stripped = moksha.filter_resources(r);

                $panel.html($stripped);
                cleanup();

                if (o.cache)
                    $.data(a, 'cache.tabs', true); // if loaded once do not load them again

                // callbacks
                $(self.element).triggerHandler('tabsload',
                    [self.fakeEvent('tabsload'), self.ui(self.$tabs[index], self.$panels[index])], o.load
                );

                // This callback is required because the switch has to take
                // place after loading has completed. Call last in order to
                // fire load before show callback...
                callback();
            }

        if (this.xhr) {
            // terminate pending requests from other tabs and restore tab label
            this.xhr.abort();
            cleanup();
        }
        $a.addClass(o.loadingClass);
        setTimeout(function() { // timeout is again required in IE, "wait" for id being restored
            self.xhr = moksha.html_load(moksha.url(url), {}, success_cb, self.$overlay_div)
        }, 0);

    },
    url: function(index, url) {
        this.$tabs.eq(index).removeData('cache.tabs').data('load.tabs', url);
    },
    destroy: function() {
        var o = this.options;
        this.element.unbind('.tabs')
            .removeClass(o.navClass).removeData('tabs');
        if (jQuery(this.element).effectivedirection() == 'rtl') {
            jQuery(this.element).removeClass(o.navClass_rtl);
        }
        this.$tabs.each(function() {
            var href = $.data(this, 'href.tabs');
            if (href)
                this.href = href;
            var $this = $(this).unbind('.tabs');
            $.each(['href', 'load', 'cache'], function(i, prefix) {
                $this.removeData(prefix + '.tabs');
            });
        });
        this.$lis.add(this.$panels).each(function() {
            if ($.data(this, 'destroy.tabs'))
                $(this).remove();
            else
                $(this).removeClass([o.selectedClass, o.unselectClass,
                    o.disabledClass, o.panelClass, o.hideClass].join(' '));
        });
    },
    fakeEvent: function(type) {
        return $.event.fix({
            type: type,
            target: this.element[0]
        });
    }
});

$.ui.mokshatabs.defaults = {
    // basic setup
    unselect: false,
    event: 'click',
    disabled: [],
    cookie: null, // e.g. { expires: 7, path: '/', domain: 'jquery.com', secure: true }
    staticLoadOnClick: false,

    // TODO history: false,

    // Ajax
    spinner: 'Loading&#8230;',
    cache: false,
    idPrefix: 'ui-tabs-',
    ajaxOptions: {},
    passPathRemainder:false,

    // animations
    fx: null, // e.g. { height: 'toggle', opacity: 'toggle', duration: 200 }



    // templates
    tabTemplate: '<li><a href="#{href}"><span>#{label}</span></a></li>',
    panelTemplate: '<div></div>',

    // CSS classes
    navClass: 'ui-tabs-nav',
    navClass_rtl: 'ui-tabs-nav-rtl',
    selectedClass: 'ui-tabs-selected',
    unselectClass: 'ui-tabs-unselect',
    disabledClass: 'ui-tabs-disabled',
    panelClass: 'ui-tabs-panel',
    hideClass: 'ui-tabs-hide',
    loadingClass: 'ui-tabs-loading',
    navContainerClass: 'moksha-ui-navcontainer'
};

$.ui.mokshatabs.getter = "length";

})(jQuery);
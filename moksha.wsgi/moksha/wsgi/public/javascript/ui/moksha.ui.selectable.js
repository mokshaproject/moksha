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
 * Moksha UI Selectable - manages a group of links so that when one is clicked
 *                        it fires off an event and adds a selected class to
 *                        the link (and removes the class from other
 *                         links)
 *
 * Copyright (c) 2009 Red Hat, Inc.
 * Dual licensed under the MIT
 * and GPLv2 licenses.
 *
 *
 * Depends:
 *      jQuery - ui.core.js
 */
(function ($) {
$.widget("ui.moksha_selectable", {

    _init: function() {
        // create selectable
        this._createselectable();

    },

    destroy: function() {

    },

    select: function(i) {
      var o = this.options;
      if (i < this.$links.length) {
         if (o.selected != i)
             if (o.selected < this.$links.length)
                 $(this.$links[o.selected]).removeClass(o.selectedClass)

         $(this.$links[i]).addClass(o.selectedClass)
      }
    },


    _createselectable: function() {
        var o = this.options;
        var $e = this.element;

        this.hover_timer = null;

        this.$links = jQuery('a', $e);

        var self = this;

        this.$links.unbind('.moksha_selectable').bind('click.moksha_selectable',
          function () {

            var i=-1;
            for (i in self.$links) {
              if (self.$links[i] === this) {
                self.select(i);
                break;
              }
            }

            if (i >= 0)
                $(self.element).triggerHandler('selected', {index: i,
                                                      element: this});
          });

        this.select(o.selected);


    }
})
$.extend($.ui.moksha_selectable, {
    version: '@VERSION',
    defaults: {
        popupClass: 'ui-moksha-selectable',
        selectedClass: 'selected',
        selected: 0
    }
});


})(jQuery);

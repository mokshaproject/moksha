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

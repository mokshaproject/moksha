jQuery(function() {
    jQuery('.widgetbrowser > ul').tabs({
        selected: null,
        unselect: true,
        select: function (ui) {
            var url = jQuery.data(ui.tab, 'load.iframe_src');
            var iframe = jQuery('iframe', ui.panel);
            if (url && !iframe.attr('src')) {
                iframe.attr('src', url);
            }
        }
    })
});

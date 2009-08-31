<div id="${id}" class="containerPlus ${draggable} ${resizable}" style="top:${top}px;left:${left}px" buttons="${buttons}" skin="${skin}" icon="${icon}" width="${width}" height="${height}" dock="${dock}">
    <div class="no">
        <div class="ne">
            <div class="n">${title}</div>
        </div>
        <div class="o">
            <div class="e">
                <div class="c">
                    <div class="content">
                      ${content}
                    % if view_source:
                      <a href="#" onclick="$('#footer')
                          .append($('<div/>')
                          .attr('id', '${id}_loader'));
                          $.ajax({
                              url: moksha.url('/widgets/code_widget?chrome=True&source=${widget_name}'),
                              success: function(r, s) {
                                  var $panel = $('#${id}_loader');
                                  var $stripped = moksha.filter_resources(r);
                                  $panel.html($stripped);
                              }
                          });
                          return false;">View Source</a>
                      % endif
                    </div>
                </div>
            </div>
        </div>
        <div>
            <div class="so">
                <div class="se">
                    <div class="s"></div>
                </div>
            </div>
        </div>
    </div>
</div>

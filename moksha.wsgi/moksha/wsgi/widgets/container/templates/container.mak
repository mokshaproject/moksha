<%namespace name="tw" module="tw2.core.mako_util"/>
<div id="${tw._('id')}" class="containerPlus ${tw._('draggable')} ${tw._('resizable')}" style="top:${str(tw._('top'))}px;left:${str(tw._('left'))}px" buttons="${tw._('buttons')}" skin="${tw._('skin')}" icon="${tw._('icon')}" width="${str(tw._('width'))}" height="${str(tw._('height'))}" dock="${tw._('dock')}">
    <div class="no">
        <div class="ne">
            <div class="n">${tw._('title')}</div>
        </div>
        <div class="o">
            <div class="e">
                <div class="c">
                    <div class="content">
                      ${tw._('content')}
                    % if tw._('view_source'):
                      <a href="#" onclick="$.ajax({
                              url: moksha.url('/widgets/code_widget?chrome=True&source=${tw._('widget_name')}'),
                              success: function(r, s) {
                                  $('body').append(moksha.filter_resources(r));
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
<script type="text/javascript">
$(document).ready(function() {
	$('#${tw._("id")}').buildContainers({
		'elementsPath': "${tw._('elementsPath')}",
		'onClose': ${tw._('onClose')},
		'onResize': ${tw._('onResize')},
		'onCollapse': ${tw._('onCollapse')},
		'onIconize': ${tw._('onIconize')},
		'onDrag': ${tw._('onDrag')},
		'onRestore': ${tw._('onRestore')},
	});
});
</script>

	<div id="${category['id']}" class="ui-sortable ${category['css_class']}">
			% for app in category['apps']:
	            <dl class="sort">
	              % if app['label']:
		    		<dt>${app['label']}</dt>
		    	  % endif
				    <dd id="${app['id']}">
                        
                    </dd>
                    <script type="text/javascript">
                          $("#${app['id']}").load("${app['url']}");
                    </script>
 				</dl>
			% endfor
		</div>

  <div id="${category['id']}" class="ui-sortable ${category['css_class']}">
      % for app in category['apps']:
              <dl class="sort">
                % if app['label']:
            <dt>${app['label']}</dt>
            % endif

            <script type="text/javascript">
               function moksha_strip_and_display(r, panel) {
                   var $temp = $(r);
                   var $scripts = $temp.find("script[src]");
                   $scripts.remove();

                  var $stripped = [];
                  $.each($temp, function(i, s) {
                                               if (!$(s).is('script[src]')){
                                                   $stripped.push(s);
                                                }
                                             });
                   panel.html($stripped);
               }
            </script>
            <dd id="${app['id']}">
                        % if app.has_key('widget'):
                            ${app['widget'](**app['params'])}
                        % endif
                    </dd>

                  % if not app.has_key('widget'):
                    <script type="text/javascript">
                          <!-- TODO: make this a JS widget -->
                          var ajaxOptions = {
                                url: "${app['url']}",
                                success: function(r, s) {
                                    var $panel = $("#${app['id']}");
                                    moksha_strip_and_display(r, $panel);
                                },
                                data: ${app['params']}
                          };

                          $.ajax(ajaxOptions);
                    </script>
                  % endif

         </dl>
      % endfor
    </div>

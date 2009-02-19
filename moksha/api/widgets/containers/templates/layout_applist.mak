  <div id="${category['id']}" class="ui-sortable ${category['css_class']}">
      % for app in category['apps']:
              <dl class="sort">
                % if app['label']:
            <dt>${app['label']}</dt>
            % endif

            <dd id="${app['id']}">
                        % if app.has_key('widget'):
                            ${app['widget'](**app['params'])}
                        % endif
                    </dd>

                  % if not app.has_key('widget'):
                    <script type="text/javascript">
                          <!-- TODO: make this a JS widget -->
                          var ajaxOptions = {
                                url: moksha.csrf_rewrite_url("${app['url']}"),
                                success: function(r, s) {
                                    var $panel = $("#${app['id']}");
                                    var $stripped = moksha.filter_resources(r);
                                    $panel.html($stripped);

                                },
                                data: ${app['params']}
                          };

                          $.ajax(ajaxOptions);
                    </script>
                  % endif

         </dl>
      % endfor
    </div>

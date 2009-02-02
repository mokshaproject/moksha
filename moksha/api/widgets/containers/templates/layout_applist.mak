  <div id="${category['id']}" class="ui-sortable ${category['css_class']}">
      % for app in category['apps']:
              <dl class="sort">
                % if app['label']:
            <dt>${app['label']}</dt>
            % endif
            <dd id="${app['id']}">
                        % if app.has_key('widget'):
                            ${app['widget'](app['params'])}
                        % endif
                    </dd>

                  % if app.has_key('url'):
                    <script type="text/javascript">
                          $("#${app['id']}").load("${app['url']}");
                    </script>
                  % endif

         </dl>
      % endfor
    </div>

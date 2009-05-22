% if category:
  <div id="${category['id']}" class="ui-sortable ${category['css_class']}">
      % for app in category['apps']:
              <div class="app ${app['css_class']}">
                % if app['label']:
            <h3>${app['label']}</h3>
            % endif
            <div id="${app['id']}_overlay" class="overlay"><div class="message"></div></div>
            <div id="${app['id']}">
                        % if app.has_key('widget'):
                            ${app['widget'](**app['params'])}
                        % endif
                    </div>

                  % if not app.has_key('widget'):
                    <script type="text/javascript">
                          <!-- TODO: make this a JS widget -->

                          var success = function(r) {
                              var $panel = $("#${app['id']}");
                              var $stripped = moksha.filter_resources(r);
                              $panel.html($stripped);
                          }

                          $(document).ready(function () {
                                                 moksha.html_load(moksha.url("${app['url']}"),
                                                                 ${app['json_params']},
                                                                 success,
                                                                 $('#${app["id"]}_overlay')
                                                                 )
                                            });
                    </script>
                  % endif

         </div>
      % endfor
    </div>
% endif
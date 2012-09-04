<%namespace name="tw" module="tw2.core.mako_util"/>
<%def name="add_panel(tabgroup)">
    % for t in tabgroup:
      % if t['type'] == 'Category':
        ${add_panel(t['apps'])}
      % elif t['type'] == 'StaticLink':
          <% pass %>
      % else:
          <div id="${t['content_id']}">
            % if t.has_key('widget'):
              ${t['widget'](**t['params'])}
            % endif
          </div>
      % endif
    % endfor
</%def>

${add_panel(tw._('tabs'))}

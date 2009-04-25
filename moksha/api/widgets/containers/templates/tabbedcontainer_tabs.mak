
<div id="${root_id}_tabs">
<%def name="display_category(cat)">
    % if cat.get('label'):
      <H4>${cat['label']}</H4>
    % endif
    <ul>
      % for t in cat['apps']:
        <li>
          ${display_tab(t)}
        </li>
      % endfor
    </ul>
</%def>

<%def name="display_tab(tab)">
    % if tab['type'] == 'Category':
        ${display_category(tab)}
    % elif tab['type'] == 'StaticLink':
        <a href="${tab['url']}${tab['query_string']}"
           title="${tab['label']}"
           class="static_link"
           >
           ${tab['label']}
        </a>
    % else:
        <a href="${tab['url']}${tab['query_string']}"
           title="${tab['label']}"
           panel="${tab['content_id']}">
          ${tab['label']}
        </a>
    % endif
</%def>

% if tabs[0]['type'] != 'Category':
    <%
       cat = {}
       cat['apps'] = tabs
    %>
    ${display_category(cat)}
% else:
    % for t in tabs:
        ${display_tab(t)}
    % endfor
% endif
</div>

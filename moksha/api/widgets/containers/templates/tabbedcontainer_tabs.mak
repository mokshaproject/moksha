
<div id="${root_id}">
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
    % else:
        <a href="${tab['url']}${tab['query_string']}" title="${tab['content_id']}">
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

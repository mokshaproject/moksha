
<div id="${root_id}">
<%def name="display_tabs(tabgroup)">
<ul>
  % for t in tabgroup:
    <li>
    % if t['type'] == 'Category':
        <H4>${t['label']}</H4>
        ${display_tabs(t['apps'])}
    % else:
        <a href="${t['url']}${t['query_string']}" title="${t['content_id']}">
          ${t['label']}
        </a>
    % endif
    </li>
  % endfor
</ul>
</%def>

${display_tabs(tabs)}
</div>

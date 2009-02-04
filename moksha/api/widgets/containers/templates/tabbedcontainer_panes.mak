% for t in tabs:
  <div id="${t['content_id']}">
    % if t.has_key('widget'):
      ${t['widget'](**t['params'])}
    % endif
  </div>
% endfor
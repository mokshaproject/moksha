<ul id="${root_id}">
  % for t in tabs:
    <li>
        <a href="${t['url']}" title="${t['content_id']}">
          ${t['label']}
        </a>
    </li>
  % endfor
</ul>

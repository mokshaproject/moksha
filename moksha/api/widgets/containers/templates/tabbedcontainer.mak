<!-- Default Template -->
<div id="${id}">
  <ul>
  % for t in tabs:
    <li><a href="${t['url']}" title="${t['label']} Page">
                    ${t['label']}
        </a>
    </li>
  % endfor
  </ul>
</div>

<!-- Default Template -->
<div>
  <ul id="${id}">
  % for t in tabs:
    <li><a href="${t['url']}" title="${t['label']} Page">
                    ${t['label']}
        </a>
    </li>
  % endfor
  </ul>
</div>
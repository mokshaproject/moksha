<!-- Default Template -->
<div>
  <ul id="${id}">
  % for t in tabs:
    <li><a href="${t[1]}" title="${t[0]} Page">
                    ${t[0]}
        </a>
    </li>
  % endfor
  </ul>
</div>
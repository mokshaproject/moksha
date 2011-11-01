<%namespace name="tw" module="moksha.utils.mako"/>
<!-- Default Template -->
<div id="${tw._('id')}">
  <ul>
  % for t in tw._('tabs'):
    <li><a href="${t['url']}" title="${t['label']} Page">
                    ${t['label']}
        </a>
    </li>
  % endfor
  </ul>
</div>

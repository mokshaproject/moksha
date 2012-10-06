<%namespace name="tw" module="tw2.core.mako_util"/>
<div class="links" id="${tw._('content_id')}">
    % for i, c in enumerate(tw._('categories')):
       % if c['label']:
         <h4>
            ${c['label']}
         </h4>
       % endif
       <ul>
       % for j, item in enumerate(c['items']):
         <li>
            <a id="${tw._('content_id')}_${i}_${j}" href="${item['link']}" moksha_url="dynamic">${item['label']}</a>
            % if 'data' in item:
            <script type="text/javascript">
                <%
                    data = item['data']
                    label = item['label']
                    if 'label' not in data:
                        data['label'] = label
                %>
                $("#${tw._('content_id')}_${i}_${j}").data('.moksha_selectable_data', ${item['data']})
            </script>
            % endif
         </li>
       % endfor
       </ul>
    % endfor
</div>

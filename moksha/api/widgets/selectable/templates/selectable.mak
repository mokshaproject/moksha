<div class="links" id="${content_id}">
    % for i, c in enumerate(categories):
       % if c['label']:
         <h4>
            ${c['label']}
         </h4>
       % endif
       <ul>
       % for j, item in enumerate(c['items']):
         <li>
            <a id="${content_id}_${i}_${j}" href="javascript:moksha.goto('${item['link']}')" >${item['label']}</a>
            % if 'data' in item:
            <script type="text/javascript">
                <%
                    data = item['data']
                    label = item['label']
                    if 'label' not in data:
                        data['label'] = label
                %>
                $("#${content_id}_${i}_${j}").data('.moksha_selectable_data', ${item['data']})
            </script>
            % endif
         </li>
       % endfor
       </ul>
    % endfor
</div>
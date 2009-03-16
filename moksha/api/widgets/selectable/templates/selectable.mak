<div class="links" id="${content_id}">
    % for c in categories:
       <h4>
            ${c['label']}
       </h4>
       <ul>
       % for c, item in enumerate(c['items']):
         <li>
            <a id="${content_id}_${c}" href="${item['link']}" >${item['label']}</a>
            % if 'data' in item:
            <script type="text/javascript">
                <%
                    data = item['data']
                    label = item['label']
                    if 'label' not in data:
                        data['label'] = label
                %>
                $("#${content_id}_${c}").data('.moksha_selectable_data', ${item['data']})
            </script>
            % endif
         </li>
       % endfor
       </ul>
    % endfor
</div>
<%namespace name="tw" module="moksha.utils.mako"/>
<div id="${tw._('id')}" class="list">
    <h3><a href="${tw._('link')}" target="_blank">${tw._('title')}</a></h3>
    <table>
        % for entry in tw._('entries'):
            <tr>
                <td id="${entry['uid']}">
                    <h4><a href="${entry.link}" target="_blank">${entry.title}</a></h4>
                    <div id="${entry['uid']}_content">
                        ${entry.content[0].value}
                    </div>
                </td>
            </tr>
        % endfor
    </table>
</div>

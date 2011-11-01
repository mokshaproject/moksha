<%namespace name="tw" module="moksha.utils.mako"/>
<div id="${tw._('id')}" class="list">
    <h3><a href="${tw._('link')}" target="_blank">${tw._('title')}</a></h3>
    <ul>
        % for entry in tw._('entries'):
            <li><a href="${entry.link}" target="_blank">${entry.title}</a></li>
        % endfor
    </ul>
</div>

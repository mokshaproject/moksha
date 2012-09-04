<%namespace name="tw" module="tw2.core.mako_util"/>
<div>
  <div id="container">
    % for c in tw._('layout'):
        ${tw._('applist_widget')(category=c)}
    % endfor
    </div>
</div>

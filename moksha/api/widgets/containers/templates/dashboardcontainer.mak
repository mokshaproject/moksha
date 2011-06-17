<%namespace name="tw" module="moksha.utils.mako"/>
<div>
  <div id="container">
    % for c in tw._('layout'):
        ${tw._('applist_widget')(category=c)}
    % endfor
    </div>
</div>

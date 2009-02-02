<div>
    Sample Template - you should subclass and create your own layout
  <div id="container">
  % for c in layout:
        ${applist_widget(category = c)}
    % endfor
    </div>

  <div id="overlay">
    <div id="preloader"><img src="/toscawidgets/resources/moksha.widgets.layout.layout/static/loader.gif" alt="" /></div>
  </div>
</div>

<html>
  <head></head>
  <body>
    % if hasattr(tmpl_context.widget, 'display'):
      ${tmpl_context.widget.display(**options)|n}
    % else:
      ${tmpl_context.widget(**options)|n}
    % endif
  </body>

  % if hasattr(tmpl_context, 'moksha_socket') and not isinstance(tmpl_context.moksha_socket, basestring) :
    ${tmpl_context.moksha_socket.display()|n}
  % endif

</html>

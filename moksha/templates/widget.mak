<html>
  <head></head>
  <body>
    % if hasattr(tmpl_context.widget, 'display'):
      ${tmpl_context.widget.display(**options)}
    % else:
      ${tmpl_context.widget(**options)}
    % endif
  </body>

  % if hasattr(tmpl_context, 'moksha_socket') and not isinstance(tmpl_context.moksha_socket, basestring) :
    ${tmpl_context.moksha_socket.display()}
  % endif

</html>

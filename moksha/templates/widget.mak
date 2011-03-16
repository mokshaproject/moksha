<html>
  <head></head>
  <body>${tmpl_context.widget.display(**options)}</body>

  % if hasattr(tmpl_context, 'moksha_socket') and not isinstance(tmpl_context.moksha_socket, basestring) :
    ${tmpl_context.moksha_socket.display()}
  % endif

</html>

<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  </head>
  <body>
    % for widget in tmpl_context.widgets:
      ${widget.display(**options.get(widget, dict()))}
    % endfor
  </body>

  % if tmpl_context.moksha_socket:
    ${tmpl_context.moksha_socket.display()}
  % endif

</html>

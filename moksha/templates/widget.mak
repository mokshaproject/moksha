<html>
  <head></head>
  <body>${tmpl_context.widget(**options)}</body>

  % if tmpl_context.moksha_socket:
    ${tmpl_context.moksha_socket()}
  % endif

</html>

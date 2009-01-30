# -*- coding: utf-8 -*-
<%namespace file="header.mak" import="*" />
<%namespace file="footer.mak" import="*" />

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <title>${title}</title>
  </head>

  <body>
    <div class="container">
      ${header()}
      <div class="span-4">
        ## Left sidebar
      </div>
      <div class="span-16">
        ## Main content
        <div id="content"></div>
      </div>
      <div class="span-4 last">
        ## Right sidebar
      </div>
      <hr class="space">
      <hr class="space">
      ${footer()}
    </div>

    ## Inject our global resources
    ${tmpl_context.moksha_global_resources()}

  </body>
</html>

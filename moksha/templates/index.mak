# -*- coding: utf-8 -*-
<%namespace file="moksha.templates.header" import="*" />
<%namespace file="moksha.templates.footer" import="*" />

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <title>${title}</title>
  </head>

  <body>
    <a cmenu="contextual_menu_default">
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
        ##<hr class="space">
        ${footer()}
      </div>
    </a>

    <div id="moksha_dock" style="display:block; padding-top: 10px; height: 30px; bottom:5px; position: absolute;" />

    ## Inject our global resources
    ${tmpl_context.moksha_global_resources() | n}

    ## Setup our right-click contextual menu
    ## ${tmpl_context.contextual_menu_widget()}

  </body>
</html>

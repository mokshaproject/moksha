def global_resources():
    """ Returns a rendered Moksha Global Resource Widget.

    This widget contains all of the resources and widgets on the
    `moksha.global` entry-point.  To use it, simply do this at the bottom of
    your master template::

        ${tmpl_context.moksha_global_resources()}

    :Warning: It must be called at the *bottom* of your template.  It must be
              the last thing that executes.  It won't inject resources for
              widgets that get displayed *after* this function is called.

    Often, you want moksha's global resources to appear on every page.
    You can override the BaseController of your app in ``yourapp.lib.base`` and
    set the following inside the __call__ method::

        from moksha.wsgi.ext.turbogears import global_resources
        tmpl_context.moksha_global_resources = global_resources

    """
    import tg
    from moksha.wsgi.widgets.api.global_resources import global_resources as globs
    globs = globs(config=tg.config, request=tg.request, base_url=tg.url('/'))

    if tg.config.default_renderer == 'genshi':
        # There's Got To Be A Better Way!
        # TODO -- consider webhelpers.literal
        from genshi import unescape, Markup
        return Markup(unescape(Markup(globs.display())))
    elif tg.config.default_renderer == 'mako':
        return globs.display()
    else:
        # If this gets called, and explodes, then you need to add support
        # for your templating engine here.
        return globs.display()

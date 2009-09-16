"""Definitions for Moksha quickstart templates"""
from paste.script.templates import Template, var
from tempita import paste_script_template_renderer

class MokshaLiveWidgetTemplate(Template):
    _template_dir = 'templates/moksha/livewidget'
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Moksha Live Widget Quickstart Template'
    #egg_plugins = ['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools']
    vars = [
            var('topic', 'The moksha topic to utilize',
                default='moksha.topics.test'),
    ]

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger

        template_engine = vars.setdefault('template_engine', 'mako')

        if template_engine == 'mako':
            # Support a Babel extractor default for Mako
            vars['babel_templates_extractor'] = \
                "('templates/**.mako', 'mako', None),\n%s#%s" % (' ' * 4,
                                                                 ' ' * 8)
        else:
            vars['babel_templates_extractor'] = ''

        vars['widget_name'] = vars['package'].title() + 'Widget'

class MokshaTemplate(Template):
    """
    Moksha default paste template class
    """
    _template_dir = 'templates/app/moksha'
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Moksha Quickstart Template'
    egg_plugins = ['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools']
    vars = [
        var('livewidget', 'Create a Moksha Live Widget example', default=False),
        var('connector', 'Create a Moksha Connector example', default=False),
        var('consumer', 'Create a Moksha Consumer example', default=False),
        var('stream', 'Create a Moksha DataStream example', default=False),
        # app (basic controller... if you want a real app, use tg2 quickstart)
        # docs (sphinx quickstart)
        # tests (tg2/tw style testing?)
    ]

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger

        template_engine = vars.setdefault('template_engine', 'mako')

        if template_engine == 'mako':
            # Support a Babel extractor default for Mako
            vars['babel_templates_extractor'] = \
                "('templates/**.mako', 'mako', None),\n%s#%s" % (' ' * 4,
                                                                 ' ' * 8)
        else:
            vars['babel_templates_extractor'] = ''

        #if vars['geo'] == 'True':
        #    # Add tgext.geo as paster plugin
        ##    vars['egg_plugins'].append('tgext.geo')

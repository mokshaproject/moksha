"""Definitions for Moksha quickstart templates"""
from paste.script.templates import Template, var
from tempita import paste_script_template_renderer

class MokshaMasterTemplate(Template):
    summary = 'Moksha Master Quickstart Template'
    _template_dir = 'templates/moksha/master'
    template_renderer = staticmethod(paste_script_template_renderer)
    vars = [
            var('livewidget', 'Include an example live widget', default=False),
            var('widget_name', 'The name of the widget', default=None),
            var('stream', 'Include an example stream', default=False),
            var('stream_name', 'The name of the stream', default=None),
            var('consumer', 'Include an exmaple consumer', default=False),
            var('consumer_name', 'The name of the consumer', default=None),
            var('connector', 'Include an example connector', default=None),
            var('connector_name', 'The name of the connector', default=None),
            var('controller', 'Include an example controller', default=None),
            var('controller_name', 'The name of the controller', default=None),
    ]

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger

        for key, value in vars.items():
            if value == 'None':
                vars[key] = None
            elif value == 'True':
                vars[key] = True
            elif value == 'False':
                vars[key] = False


class MokshaLiveWidgetTemplate(Template):
    _template_dir = 'templates/moksha/livewidget'
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Moksha Live Widget Quickstart Template'
    egg_plugins = ['Moksha']
    vars = [
            var('topic', 'The moksha topic to utilize',
                default='moksha.topics.test'),
            var('livewidget', 'Include an example live widget', default=False),
            var('widget_name', 'The name of the widget', default=None),
    ]

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        if 'widget_name' not in vars:
            vars['widget_name'] = vars['project'].title() + 'Widget'

class MokshaStreamTemplate(Template):
    summary = 'Moksha Stream Quickstart Template'
    _template_dir = 'templates/moksha/stream'
    template_renderer = staticmethod(paste_script_template_renderer)
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
        vars['stream_name'] = vars['package'].title() + 'Stream'


class MokshaConsumerTemplate(Template):
    summary = 'Moksha Consumer Quickstart Template'
    _template_dir = 'templates/moksha/consumer'
    template_renderer = staticmethod(paste_script_template_renderer)
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
        vars['consumer_name'] = vars['package'].title() + 'Consumer'


class MokshaConnectorTemplate(Template):
    summary = 'Moksha Connector Quickstart Template'
    _template_dir = 'templates/moksha/connector'
    template_renderer = staticmethod(paste_script_template_renderer)
    vars = []

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        vars['connector_name'] = vars['package'].title() + 'Connector'


class MokshaControllerTemplate(Template):
    summary = 'Moksha Controller Quickstart Template'
    _template_dir = 'templates/moksha/controller'
    template_renderer = staticmethod(paste_script_template_renderer)
    vars = []

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        vars['controller_name'] = vars['package'].title() + 'Controller'

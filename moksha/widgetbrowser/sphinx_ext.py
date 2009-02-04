import os
from docutils import nodes, utils
from docutils.parsers.rst import directives

from widgetbrowser import util, widgets

widget_tabs = widgets.WidgetBrowserTabs(in_sphinx=True)

def widgetbrowser_directive(dirname, arguments, options, content, lineno,
                            content_offset, block_text, state, state_machine):
    """Processes the `widgetbrowser` reStructuredText directive.
    
    When generating the URL for the widget it peeks into os.environ for the
    'TW_BROWSER_PREFIX' environment variable.
    """
    widget_path = arguments[0]
    widget = util.import_widget(widget_path)
    if not widget:
        reporter = state.document.reporter
        msg = reporter.warning(
            'No widget found at %r' % widget_path, line=lineno)
        prb = nodes.problematic(block_text, block_text, msg)
        return [msg, prb]
    tabs = options.get('tabs') or widget_tabs.tabs
    prefix = os.environ.get('TW_BROWSER_PREFIX')
    size = options.get('size')
    html = widget_tabs(widget, tabs=tabs, prefix=prefix, size=size)
    node = nodes.raw('', html, format='html')
    return [node]


def _get_tabs(arg):
    if arg is None:
        return []
    return [s.strip() for s in arg.split(',')]
    
def _get_size(arg):
    return arg or "small"

def setup(app):
    browser_options = {'tabs': _get_tabs, 'size':_get_size}
    app.add_directive('widgetbrowser', widgetbrowser_directive, 1, (1, 0, 1),
                      **browser_options)

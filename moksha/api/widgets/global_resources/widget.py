import logging
import pkg_resources

from inspect import isclass
from tw.api import Widget, CSSLink, JSLink

log = logging.getLogger(__name__)

class GlobalResourceInjectionWidget(Widget):
    """
    Injects all global resources, such as JavaScript and CSS, on every page.
    This widget will pull in all JSLink and CSLink widgets that are listed
    on the `[moksha.global]` entry-point.
    """
    javascript = []
    children = []
    css = []
    template = """
        % for child in c:
            ${child()}
        % endfor
    """
    engine_name = 'mako'

    def __init__(self):
        super(GlobalResourceInjectionWidget, self).__init__()
        for widget_entry in pkg_resources.iter_entry_points('moksha.global'):
            log.info('Loading global resource: %s' % widget_entry.name)
            loaded = widget_entry.load()
            if isclass(loaded):
                loaded = loaded(widget_entry.name)
            if isinstance(loaded, JSLink):
                self.javascript.append(loaded)
            elif isinstance(loaded, CSSLink):
                self.css.append(loaded)
            elif isinstance(loaded, Widget):
                self.children.append(loaded)
            else:
                raise Exception("Unknown global resource: %s.  Should be "
                                "either a JSLink or CSSLink." %
                                widget_entry.name)

global_resources = GlobalResourceInjectionWidget()

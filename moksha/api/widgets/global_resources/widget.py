import logging
import pkg_resources

from inspect import isclass
from tw.api import Widget, CSSLink, JSLink

log = logging.getLogger(__name__)

class GlobalResourceInjectionWidget(Widget):
    """
    This widget will pull in all JSLink, CSSLink, and Widget resources that
    are listed on the `[moksha.global]` entry-point.

    :Note: Global Widget injection will only work when the global_resource
           widget is actually rendered in the template.  Otherwise, only JS
           and CSS resources fill get injected.  Moksha's index.mak template
           handles this for us, otherwise you can import the `global_resources`
           widget from this module and do it yourself.
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

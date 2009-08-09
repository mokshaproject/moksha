import sys
import weakref
import os
import inspect
import logging
from pkg_resources import resource_filename
from genshi.core import Markup
from genshi.template import TemplateLoader, Context
from webob import Request, Response, exc
import tw
from tw.api import Widget, WidgetType, make_middleware
from moksha.apps.widgetbrowser import util, widgets, repl

try:
    from formencode import Invalid
    have_formencode = True
except ImportError:
    have_formencode = False

from moksha.lib.helpers import cache_rendered

__all__ = ['WidgetBrowser']

log = logging.getLogger(__name__)

def asbool(v):
    if isinstance(v, basestring):
        return v.lower().startswith('t') or v == '1' or v == 'on'
    elif isinstance(v, bool):
        return v
    return False

class WidgetBrowser(object):
    """A widget browser WSGI app.

    Parameters:

      * `template_dirs`: A list of directories that shall be searched for
        temlates used by the widget browser.
      * `interactive`: Enable code execution. This is needed to for the REPL and
        to override display arguments via the web interface. This is a BIG
        SECURITY HOLE, enable only in a controlled environment.
      * `docs_dir`: A directory where sphinx sources live.
    """
    def __init__(self, global_conf={}, template_dirs=None, interactive=False,
                 docs_dir=None, full_stack=True):
        if isinstance(template_dirs, basestring):
            template_dirs = template_dirs.split()
        template_dirs = template_dirs or []
        template_dirs.append(resource_filename('moksha.apps.widgetbrowser', 'templates'))
        self.loader = TemplateLoader(template_dirs)
        self.interactive = asbool(interactive)
        if self.interactive:
            self.http_repl = repl.WidgetReplApp(globals(), weakref.proxy(self))
            self.context = self.http_repl.repl.locals
        else:
            self.context = None
            self.http_repl = exc.HTTPForbidden("Interactive mode is disabled")
        if docs_dir:
            from paste.cascade import Cascade
            dest_dir = os.path.abspath(os.path.join(docs_dir))
            #log.info('Building docs...')
            #try:
            #    util.build_docs(docs_dir, dest_dir)
            #except Exception, e:
            #    log.warning('Skipping building docs: %s' % str(e))
            self.built_docs = dest_dir
            self.app = Cascade([self.docs_app, self.app])
        if asbool(full_stack):
            self.app = make_middleware(self.app, {
                'toscawidgets.framework.default_view': 'genshi',
                }, stack_registry = True)
        self._default_controllers = dict(demo=self.show_demo,
                                         index=self.show_index,
                                         template=self.show_template,
                                         parameters=self.show_parameters,
                                         source=self.show_source,
                                         demo_source=self.show_demo_source)


    def docs_app(self, environ, start_response):
        """Registers widgetbrowser_js as resources before serving static html
        files so it is injected into the page"""
        from paste.urlparser import StaticURLParser
        app = StaticURLParser(self.built_docs)
        resources = widgets.widgetbrowser_js.retrieve_resources()
        tw.framework.register_resources(resources)
        return app(environ, start_response)

    _widget_controllers = {}
    @classmethod
    def register_controller(cls, widget, action):
        """Registers function to act as a demo controller for a widget"""
        def _register(controller):
            cls._widget_controllers[(widget,action)] = controller
            return controller
        return _register

    def lookup_controller(self, widget_cls, action):
        try:
            return self._widget_controllers[(widget_cls, action)]
        except KeyError:
            return self._default_controllers[action]

    def lookup_widget_action(self, path_info):
        try:
            widget_path, action = path_info.strip('/').split('/')
        except ValueError:
            widget_path, action = path_info, 'index'
        if widget_path:
            try:
                widget = util.import_widget(widget_path.strip('/'))
            except (ImportError, ValueError):
                widget = None
            if widget:
                return widget, action
        raise LookupError(path_info)

    def render(self, template, ns):
        ns.pop('self',None)
        stream = self.loader.load(template).generate(Context(**ns))
        return stream.render(method='xhtml', doctype='xhtml')

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

    #@cache_rendered
    def app(self, environ, start_response):
        req = Request(environ)
        resp = Response(request=req, content_type='text/html; charset=utf-8')
        # Leave the interactive flag in tw.framework so demo controllers can know
        # if it is safe to enable advanced/unsecure features.
        tw.framework.request_local.interactive = self.interactive
        tw.framework.request_local.browser_prefix = req.script_name

        # Lookup widget XXX: Yuck!
        if req.path_info == '/':
            controller = self.home
        elif req.path_info.startswith('/_repl') and self.http_repl:
            req.path_info_pop()
            return self.http_repl(environ, start_response)
        elif req.path_info.startswith('/widgets'):
            controller = self.widgets
        else:
            try:
                widget, action = self.lookup_widget_action(req.path_info)
            except LookupError:
                resp = exc.HTTPNotFound('No widget at %s' % req.path_info)
                return resp(environ, start_response)
                

            # Lookup controller
            try:
                controller = self.lookup_controller(widget, action)
            except LookupError:
                resp = exc.HTTPNotImplemented()
                return resp(environ, start_response)
                
            # If it's a widget class instantiate it with no arguments 
            if isinstance(widget, WidgetType):
                widget = widget('test_widget')
            req.widget = widget

        # Call controller and handle output 
        output = controller(req, resp)
        if isinstance(output, str):
            resp.body = output
        elif isinstance(output, unicode):
            resp.body = output.encode('utf-8')
        elif output:
            resp = output

        return resp(environ, start_response)


    def show_template(self, req, resp):
        widget = req.widget
        if getattr(widget, 'demo_for', None):
            widget = req.widget.demo_for()
        template = util.widget_template(widget)
        if template:
            return util.format_code(template, 'html')
        else:
            resp.content_type = "text/plain"
            return widget.__class__.__name__ + ' has no template.'

    def show_source(self, req, resp):
        cls = getattr(req.widget, 'demo_for', req.widget.__class__)
        source = inspect.getsource(cls)
        return util.format_code(source, 'python')

    def show_demo_source(self, req, resp):
        widget = req.widget
        source = inspect.getsource(widget.__class__)
        return util.format_code(source, 'python')

    def show_parameters(self, req, resp):
        cls = getattr(req.widget, 'demo_for', req.widget.__class__)
        parameters = util.WidgetParameters(cls)
        return self.render('widget_parameters.html', locals())


    def show_index(self, req, resp):
        widget = req.widget
        return self.render('widget_index.html', locals())

    @cache_rendered
    def show_demo(self, req, resp):
        widget = req.widget
        widget_name = widget.__class__.__name__
        interactive = self.interactive
        if have_formencode and req.method.upper() == "POST":
            # A widget submission, try to validate.
            try:
                value = widget.validate(req.POST)
                value = util.pretty_print(value)
                return self.render('validation_result.html', locals())
            except Invalid, error:
                pass

        if self.interactive:
            _disp = req.GET.get('_disp', '')
        else:
            _disp = ''

        widget_output = util.display_widget(widget, _disp, self.context)

        # Wrap non-genshi things, like Mako based widgets, in a Genshi Markup object
        if not callable(widget_output):
            widget_output = Markup(widget_output)

        # Inject moksha's global resources so we can get things like
        # Orbited/Stomp/jQuery/etc.
        from moksha.api.widgets.global_resources import global_resources
        global_resources.register_resources()

        return self.render('show_widget.html', locals())

    def widgets(self, req, resp):
        widgets = [(util.widget_path(w), util.widget_url(w))
                       for w in util.all_widgets()]
        widgets.sort()
        return self.render('list_widgets.html', locals())

    def home(self, req, resp):
        widgets.jquery_js.inject()
        widgets.tabs_css.inject()
        widgets.ui_tabs_js.inject()
        def url(s):
            return req.script_name + s
        return self.render('home.html', locals())

"""
Robert Brewer was the original author of the module this module has heavily
inspired from.  http://www.aminus.net/wiki/HTTPREPL
"""
import warnings
from itertools import count
import codeop
import inspect
import os
import re

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import sys
import traceback

from webob import Request, Response, exc

try:
    from formencode import Invalid
    have_formencode = True
except ImportError:
    have_formencode = False

from genshi.util import LRUCache
import tw
from tw.api import make_middleware, Widget

from moksha.widgetbrowser import util, widgets

class HTTPREPL:
    
    def __init__(self, locals=None):
        self.locals = {}
        if locals:
            self.locals.update(locals)
        self.buffer = []
    
    def push(self, line):
        """Push 'line' and return exec results (None if more input needed)."""
        if line == "help":
            return "Type help(object) for help about object."
        if line == "help()":
            return "You cannot call help() without an argument."
        
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        
        try:
            code = codeop.compile_command(source, "<HTTP input>", 'single')
        except (OverflowError, SyntaxError, ValueError):
            self.buffer = []
            return traceback.format_exc()
        
        if code is None:
            # More lines needed.
            return None
        
        self.buffer = []
        return self.execute(code)
    
    def execute(self, code):
        """Execute the given code in self.locals and return any stdout/sterr."""
        out = StringIO()
        oldout = sys.stdout
        olderr = sys.stderr
        sys.stdout = sys.stderr = out
        try:
            try:
                exec code in self.locals
            except:
                result = traceback.format_exc()
            else:
                result = out.getvalue()
        finally:
            # FormEncode will break if _ is left in __builtins__ and it tries
            # to use it as a translator
            __builtins__.pop('_', None)
            sys.stdout = oldout
            sys.stderr = olderr
        out.close()
        return result
    
    def dir(self, line):
        """Examine a partial line and provide attr list of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "thing.attr" as "thing.", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = ".".join(line.split(".")[:-1])
        try:
            result = eval("dir(%s)" % line, {}, self.locals)
        except:
            return []
        return result
    
    def doc(self, line):
        """Examine a partial line and provide sig+doc of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "func(text" as "func(", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = "(".join(line.split("(")[:-1])
        try:
            result = eval(line, {}, self.locals)
            try:
                if isinstance(result, type):
                    func = result.__init__
                else:
                    func = result
                args, varargs, varkw, defaults = inspect.getargspec(func)
            except TypeError:
                if callable(result):
                    doc = getattr(result, "__doc__", "") or ""
                    return "%s\n\n%s" % (line, doc)
                return None
        except:
            return None
        
        if args and args[0] == 'self':
            args.pop(0)
        missing = object()
        defaults = defaults or []
        defaults = ([missing] * (len(args) - len(defaults))) + list(defaults)
        arglist = []
        for a, d in zip(args, defaults):
            if d is missing:
                arglist.append(a)
            else:
                arglist.append("%s=%s" % (a, d))
        if varargs:
            arglist.append("*%s" % varargs)
        if varkw:
            arglist.append("**%s" % varkw)
        doc = getattr(result, "__doc__", "") or ""
        return "%s(%s)\n%s" % (line, ", ".join(arglist), doc)


class DeferredDisplay(object):
    """Wraps a widget and the args passed to display/render so we can defer
    its display to another request.
    
    .. note::
        The JS code is dependent on the output of __repr__ since it parses it
        to know a widget is being displayed so it can open an overlay.
    """
    _counter = count(0)
    def __init__(self, widget, value, **kw):
        self.id = self._counter.next()
        self.value = value
        self.widget = widget
        self.kw = kw

    def display(self):
        """
        Displays the widget as it was intended to be displayed when it was
        wrapped.
        """
        return self.widget.display(self.value, **self.kw)

    __call__ = display

    def __repr__(self):
        data = (self.id, self.widget.__class__)
        return self.__class__.__name__ + repr(data)


class WidgetReplApp(object):
    def __init__(self, locals=None, widget_browser=None, max_dialogs=10):
        self.repl = HTTPREPL(locals)
        warnings.warn("\n"*2 + "*"*79 + "\n"
                      "DISCLAIMER:\n"
                      "Running this app poses a significant security threat "
                      "if accessible to an \nattacker. Make sure the server is "
                      "bound to the loopback interface or behind\na firewall "
                      "and that there are no local untrusted users.\n" + "*"*79)
        if widget_browser:
            self.widget_browser = widget_browser
            self.displayed_widgets = LRUCache(max_dialogs)
            self.setup_tw()

    def setup_tw(repl_app):
        # Stack TW's middleware configured with dummy default_view to signal
        # that a widget is being displayed so we can wrap and register its
        # output.
        conf = {'toscawidgets.framework.default_view' : 'tw_repl',
                'toscawidgets.middleware.inject_resources' : True}
        repl_app.app = make_middleware(repl_app.app, conf)
        # monkey-patch display and render to hijack output
        def wrap(f):
            if f.func_name == 'wrapper':
                return f
            def wrapper(self, value=None, **kw):
                if self.displays_on == 'tw_repl':
                    o = DeferredDisplay(self, value, **kw)
                    repl_app.displayed_widgets[o.id] = o
                else:
                    o = f(self, value, **kw)
                return o
            return wrapper
        Widget.display = wrap(Widget.display)
        Widget.render = wrap(Widget.render)

    def __call__(self, environ, start_response):
        assert not environ['wsgi.multiprocess'], "Cannot run in a multiprocess"\
                                                 " environment"
        return self.app(environ, start_response)

    def app(self, environ, start_response):
        """Main dispatcher. pops PATH_INFO and delegates to exposed methods."""
        req = Request(environ.copy())
        resp = Response(request=req, content_type='text/html; charset=UTF8')
        first_part = req.path_info_pop() or 'index'
        method = getattr(self, first_part, None)
        if getattr(method, 'exposed', False):
            output = method(req, resp)
            if isinstance(output, unicode):
                resp.body = output.encode('utf-8')
            elif isinstance(output, str):
                resp.body = output
            elif output:
                resp = output
        else:
            resp = exc.HTTPNotImplemented()
        return resp(environ, start_response)
        
    def index(self, req, resp):
        """Return an HTTP-based Read-Eval-Print-Loop terminal."""
        # Override default_view so resources display properly
        tw.framework.default_view = 'toscawidgets'
        tpl = '<html><head><title>"%(title)s</title></head>' \
              '<body class="flora">%(repl)s</body></html>'
        prefix = req.script_name + '/'
        return tpl % {'title': 'WidgetBrowser Terminal',
                      'repl': widgets.repl(prefix=req.script_name + '/')}
    index.exposed = True
    
    def push(self, req, resp):
        """Push 'line' and return exec results as a bare response."""
        line = req.params['line']
        result = self.repl.push(line)
        if result is None:
            # More input lines needed.
            resp.status_int = 204
        return result
    push.exposed = True
    
    def dir(self, req, resp):
        """Push 'line' and return result of eval on the final expr."""
        line = req.params['line']
        result = self.repl.dir(line)
        if not result:
            resp.status_int = 204
            return
        return repr(result)
    dir.exposed = True
    
    def doc(self, req, resp):
        """Push 'line' and return result of getargspec on the final expr."""
        line = req.params['line']
        result = self.repl.doc(line)
        if not result:
            resp.status_int = 204
        return result
    doc.exposed = True
    
    def enrich_namespace(self, ns, request):
        
        _disp = request.GET.get('_disp', '')
        
        if not "_disp" in ns:
            ns["_disp"]=_disp
        if not "interactive" in ns:
            ns["interactive"]=True
        return ns
    
    def widget_output(self, req, resp):
        try:
            key = int(req.path_info.strip('/'))
            dd = self.displayed_widgets[key]
        except KeyError:
            resp.status_int = 404
            return "There's now widget output at this URL. Maybe it has "\
                   "expired? Try increasing the 'max_dialogs' parameter"

        widget = dd.widget
        widget_name = widget.__class__.__name__
        render = self.widget_browser.render
        if have_formencode and req.method.upper() == "POST":
            # A widget submission, try to validate.
            try:
                value = widget.validate(req.POST)
                value = util.pretty_print(value)
                return render('validation_result.html', locals())
            except Invalid, error:
                pass
        # Override default_view because WidgetBrowser renders on Genshi, not
        # 'tw_repl', this is needed so widget and resources display properly
        tw.framework.default_view = 'genshi'
        widget_output = dd.display()
        return render('show_widget.html', self.enrich_namespace(locals(),request=req))
    widget_output.exposed = True

from wsgiref.simple_server import make_server
from optparse import OptionParser

from moksha.apps.widgetbrowser.wsgiapp import WidgetBrowser


_parser = OptionParser(usage = "%prog [OPTIONS] [widget_url]")
_parser.add_option("-i", "--interactive",
                   dest="interactive",
                   action="store_true",
                   default=False)
_parser.add_option("-b", "--browser",
                   dest="browser",
                   action="store_true",
                   default=False)
_parser.add_option("-d", "--docs",
                   dest="docs",
                   default=None)
_parser.add_option("-p", "--port",
                   dest="port",
                   default=8000)

def browser_command(argv=None):
    """Command line interface to launch the widgetbrowser"""
    opts, args = _parser.parse_args(argv)

    # Only allow passing display arguments in debug mode 
    if args:
        widget_url = args[0] + '/'
    else:
        widget_url = ''
    app = WidgetBrowser(interactive=opts.interactive, docs_dir=opts.docs)
    if opts.interactive:
        try:
            from weberror.evalexception import EvalException
            app = EvalException(app)
        except ImportError:
            raise ImportError("You need to install WebError for interactive "
                              "debugging")
    url = "http://127.0.0.1:%s/" % opts.port
    if opts.browser:
        import webbrowser
        webbrowser.open(url + widget_url)
    server = make_server('127.0.0.1', int(opts.port), app)
    print "Server started at " + url
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    import sys
    sys.exit(browser_command(sys.argv))


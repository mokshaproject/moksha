from tw.api import Widget

class HelloWorldWidget(Widget):
    params = ['msg']
    msg = 'Hello World'
    template = '${msg}'
    engine_name = 'mako'

    def update_params(self, d):
        """ Render-time logic """
        super(HelloWorldWidget, self).update_params(d)

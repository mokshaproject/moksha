from tg import expose

class Root(object):

    @expose()
    def index(self, *args, **kwargs):
        return 'Hello World!'

    @expose('mako:demo.template')
    def mako(self, *args, **kwargs):
        """ An example controller method exposed with a Mako template """
        return {'msg': 'Hello World!'}

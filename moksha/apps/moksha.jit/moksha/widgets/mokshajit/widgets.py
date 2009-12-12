from moksha.api.widgets.live import LiveWidget

class MokshaJitWidget(LiveWidget):
    topic = 'moksha.jit'
    params = ['id']
    onmessage = "$('<div/>').text(json.message).appendTo('#${id}');"
    template = 'mako:moksha.widgets.mokshajit.templates.widget'

    def update_params(self, d):
        super(Moksha.JitWidget, self).update_params(d)

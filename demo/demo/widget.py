from moksha.api.widgets.live import LiveWidget

class HelloWorldWidget(LiveWidget):
    topic = "helloworld"
    onmessage = "$('#data').append(json.msg).append('<br/>');"
    template = """
        <b>Hello World Widget</b>
        <div id="data"/>
    """

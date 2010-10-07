from moksha.api.widgets.live import LiveWidget

class HelloWorldWidget(LiveWidget):
    topic = "helloworld"
    template = """
        <b>Hello World Widget</b>
        <div id="data"/>
    """
    onmessage = "$('#data').append(json.msg).append('<br/>');"

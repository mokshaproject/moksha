from moksha.api.widgets.live import LiveWidget

class HelloWorldWidget(LiveWidget):
    topic = "helloworld"
    template = """
        <b>Hello World Widget</b>
        <ul id="data"/>
    """
    onmessage = """
        $('<li/>').text(json.msg).prependTo('#data');
    """

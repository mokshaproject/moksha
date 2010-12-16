from moksha.api.widgets.live import LiveWidget

class HelloWorldWidget(LiveWidget):
    topic = "helloworld"
    template = """
        <b>Hello World Widget</b>
        <form onsubmit="return send_msg()">
            <input name="text" id="text"/>
        </form>

        <ul id="data"/>

        <script>
            function send_msg() {
                moksha.send_message('helloworld', {'msg': $('#text').val()});
                $('#text').val('');
                return false;
            }
        </script>
    """
    onmessage = """
        $('<li/>').text(json.msg).prependTo('#data');
    """

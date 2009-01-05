from tw.api import Widget, CSSLink, JSLink, js_callback, js_function
from tw.jquery import jquery_js
from moksha.stomp import stomp_widget, stomp_subscribe

class LiveGraphWidget(Widget):
    """
    This is an example live graph widget based on Michael Carter's article
    "Scalable Real-Time Web Architecture, Part 2: A Live Graph with Orbited,
    MorbidQ, and js.io".

    http://cometdaily.com/2008/10/10/scalable-real-time-web-architecture-part-2-a-live-graph-with-orbited-morbidq-and-jsio
    """
    params = ['onconnectedframe', 'onmessageframe']
    onconnectedframe = stomp_subscribe('/topic/graph')
    onmessageframe = js_callback('function(f){ modify_graph(bars, f.body) }')
    javascript = [JSLink(filename='static/livegraph.js', modname=__name__)]
    css = [CSSLink(filename='static/livegraph.css', modname=__name__)]
    children = [stomp_widget]
    template = """
        <div id="livegraph"></div>
        ${c.stomp(onmessageframe=onmessageframe,
                  onconnectedframe=onconnectedframe)}
    """
    engine_name = 'mako'

    def update_params(self, d):
        super(LiveGraphWidget, self).update_params(d)
        self.add_call(js_function('init_graph')('livegraph'))


from tw.jquery.flot import FlotWidget

class LiveFlotWidget(Widget):
    children = [stomp_widget, FlotWidget('flot')]
    params = ['id', 'height', 'width', 'onconnectedframe', 'onmessageframe']
    onconnectedframe = stomp_subscribe('/topic/flot_example')
    onmessageframe = js_callback("""function(frame){
            var data = JSON.parse(frame.body)[0];
            $.plot($("#liveflot"), data["data"], data["options"]);
    }""")
    template = """
        <div id="${id}" style="width:${width};height:${height};"/>
        ${c.stomp(onmessageframe=onmessageframe,
                  onconnectedframe=onconnectedframe)}
    """
    engine_name = 'mako'
    height = '300px'
    width = '500px'

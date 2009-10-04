import tw.jquery.jqplot
from tw.jquery.jqplot import AsynchronousJQPlotWidget, JQPlotWidget
from moksha.api.widgets.live import LiveWidget

class LiveJQPlotWidget(JQPlotWidget, LiveWidget):
    """ A live plotting Widget, powered by Moksha & tw.jquery.JQPlot

    :topic: The topic stream to listen to
    :onmessage: Javascript that is called with new messages as they arrive
    """
    onmessage = AsynchronousJQPlotWidget.callback_reset % '${id}'
    topic = None


plot_widget = LiveJQPlotWidget(id='plot_widget',
        extra_js=[tw.jquery.jqplot.jqp_dateAxis_js],
        topic='jqplot.demo.plot')


pie_widget = LiveJQPlotWidget(id='pie_widget',
        extra_js=[tw.jquery.jqplot.jqp_pie_js],
        width='300px', height='300px',
        topic='jqplot.demo.pie')

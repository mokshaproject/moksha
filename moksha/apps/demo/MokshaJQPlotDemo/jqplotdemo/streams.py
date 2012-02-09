from moksha.api.hub.producer import PollingProducer
from jqplotdemo.controllers.plots import get_plot_data, make_data, get_pie_data

class JQPlotDemoStream(PollingProducer):
    frequency = 1.0

    def poll(self):
        self.send_message('jqplot.demo.plot', get_plot_data())
        self.send_message('jqplot.demo.pie', get_pie_data())

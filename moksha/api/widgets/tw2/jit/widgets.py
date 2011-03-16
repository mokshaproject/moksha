# Authors: Ralph Bean <ralph.bean@gmail.com

from tw.jquery.flot import flot_js, excanvas_js, flot_css
from moksha.api.widgets import TW2LiveWidget
from tw2.jit import AreaChart

class LiveAreaChartWidget(AreaChart, TW2LiveWidget):
    """ A live graphing widget using tw2.jit """
    onmessage = 'window._jitwidgets["${id}"].loadJSON(json[0])'

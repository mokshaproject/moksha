# Authors: Ralph Bean <rbean@redhat.com>

from moksha.wsgi.widgets.api import LiveWidget
from tw2.jit import AreaChart


class LiveAreaChartWidget(AreaChart, LiveWidget):
    """ A live graphing widget using tw2.jit """
    onmessage = 'window._jitwidgets["${id}"].loadJSON(json[0])'

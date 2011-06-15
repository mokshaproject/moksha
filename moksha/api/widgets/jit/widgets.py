# Authors: Ralph Bean <ralph.bean@gmail.com

from tw.jquery.flot import flot_js, excanvas_js, flot_css
from moksha.api.widgets import TW2LiveWidget
from tw2.jit import AreaChart

from tg import config
from paste.deploy.converters import asbool


class TW2LiveAreaChartWidget(AreaChart, TW2LiveWidget):
    """ A live graphing widget using tw2.jit """
    onmessage = 'window._jitwidgets["${id}"].loadJSON(json[0])'


if asbool(config.get('moksha.use_tw2', False)):
    LiveAreaChartWidget = TW2AreaChartWidget
else:
    # Probably never will be
    raise NotImplementedError(__name__ + " is not ready for tw1")

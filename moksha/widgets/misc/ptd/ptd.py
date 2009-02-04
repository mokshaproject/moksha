# Processed Tower Defense Widget

from tw.api import Widget, CSSLink, JSLink
from tw.jquery.ui import effects_core_js, effects_highlight_min_js
from tw.jquery.processing import processing_js

modname = __name__

jsfprocessing_js = JSLink(filename='static/jsfprocessing.js',
                          javascript=[processing_js],
                          modname=modname)

# lulz
konami = JSLink(filename='static/konami.js', modname=modname)

class ProcessedTowerDefense(Widget):
    name = 'Processed Tower Defense'
    hidden = True
    template = 'mako:moksha.widgets.misc.ptd.templates.ptd'
    css = [CSSLink(filename='static/style.css', modname=modname),]
    javascript = [
            processing_js, jsfprocessing_js,
            effects_core_js, effects_highlight_min_js,
            JSLink(filename='game/creep_waves.js', modname=modname),
            JSLink(filename='game/terrain.js', modname=modname),
            JSLink(filename='game/util.js', modname=modname),
            JSLink(filename='game/creeps.js', modname=modname),
            JSLink(filename='game/ui_modes.js', modname=modname),
            JSLink(filename='game/weapons.js', modname=modname),
            JSLink(filename='game/ptd.js', modname=modname),
            ]

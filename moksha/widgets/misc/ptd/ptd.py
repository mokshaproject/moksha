# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Processed Tower Defense Widget

from tw.api import Widget, CSSLink, JSLink
from tw.jquery.ui import effects_core_js, effects_highlight_js
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
            effects_core_js, effects_highlight_js,
            JSLink(filename='game/creep_waves.js', modname=modname),
            JSLink(filename='game/terrain.js', modname=modname),
            JSLink(filename='game/util.js', modname=modname),
            JSLink(filename='game/creeps.js', modname=modname),
            JSLink(filename='game/ui_modes.js', modname=modname),
            JSLink(filename='game/weapons.js', modname=modname),
            JSLink(filename='game/ptd.js', modname=modname),
            ]

# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

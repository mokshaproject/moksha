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
#
# Authors: Luke Macken <lmacken@redhat.com>

""" ToscaWidget's for the Blueprint CSS Framework """

from tw.api import CSSLink, IECSSLink

modname = __name__

blueprint_screen_css = CSSLink(modname=modname,
                               filename='static/screen.css',
                               media='screen, projection')

blueprint_print_css = CSSLink(modname=modname,
                              filename='static/print.css',
                              media='print')

blueprint_ie_css = IECSSLink(modname=modname,
                             filename='static/ie.css',
                             media='screen, projection')

##
## Blueprint Plugins
##

# Gives you some great CSS-only buttons.
blueprint_plugin_buttons_css = CSSLink(modname=modname,
        filename='static/plugins/buttons/screen.css')

# Gives you classes to use if you'd like some extra fancy typography.
blueprint_plugin_fancytype_css = CSSLink(modname=modname,
        filename='static/plugins/fancy-type/screen.css')

# Icons for links based on protocol or file type.
blueprint_plugin_linkicons_css = CSSLink(modname=modname,
        filename='static/plugins/link-icons/screen.css',
        media='screen, projection')

# Mirrors Blueprint, so it can be used with Right-to-Left languages.
blueprint_plugin_rtl_css = CSSLink(modname=modname,
        filename='static/plugins/rtl/screen.css',
        media='screen, projection')

# Blueprint Silk Sprite
# * Silk Sprite is Based on the Silk Icon Set by Mark James [famfamfam.com] 
# * Compiled & Adapted for Blueprint by Don Albrecht [ajaxbestiary.com]
# * Usage released under a creative commons Attribution 2.5 license
#   http://creativecommons.org/licenses/by/2.5/
blueprint_sprites_css = CSSLink(modname=modname,
        filename='static/plugins/sprites/sprite.css',
        media='screen')

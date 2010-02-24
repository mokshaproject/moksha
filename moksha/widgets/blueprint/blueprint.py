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

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

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw2.core as twc

modname = __name__


tw1_blueprint_screen_css = tw.api.CSSLink(
    modname=modname,
    filename='static/screen.css',
    media='screen, projection')

tw1_blueprint_print_css = tw.api.CSSLink(
    modname=modname,
    filename='static/print.css',
    media='print')

tw1_blueprint_ie_css = tw.api.IECSSLink(
    modname=modname,
    filename='static/ie.css',
    media='screen, projection')

##
## Blueprint Plugins
##

# Gives you some great CSS-only buttons.
tw1_blueprint_plugin_buttons_css = tw.api.CSSLink(
    modname=modname,
    filename='static/plugins/buttons/screen.css')

# Gives you classes to use if you'd like some extra fancy typography.
tw1_blueprint_plugin_fancytype_css = tw.api.CSSLink(
    modname=modname,
    filename='static/plugins/fancy-type/screen.css')

# Icons for links based on protocol or file type.
tw1_blueprint_plugin_linkicons_css = tw.api.CSSLink(
    modname=modname,
    filename='static/plugins/link-icons/screen.css',
    media='screen, projection')

# Mirrors Blueprint, so it can be used with Right-to-Left languages.
tw1_blueprint_plugin_rtl_css = tw.api.CSSLink(
    modname=modname,
    filename='static/plugins/rtl/screen.css',
    media='screen, projection')

# Blueprint Silk Sprite
# * Silk Sprite is Based on the Silk Icon Set by Mark James [famfamfam.com]
# * Compiled & Adapted for Blueprint by Don Albrecht [ajaxbestiary.com]
# * Usage released under a creative commons Attribution 2.5 license
#   http://creativecommons.org/licenses/by/2.5/
tw1_blueprint_sprites_css = tw.api.CSSLink(
    modname=modname,
    filename='static/plugins/sprites/sprite.css',
    media='screen')


# tw2 equivalents
tw2_blueprint_screen_css = twc.CSSLink(
    modname=modname,
    filename='static/screen.css',
    media='screen, projection')

tw2_blueprint_print_css = twc.CSSLink(
    modname=modname,
    filename='static/print.css',
    media='print')

tw2_blueprint_ie_css = twc.CSSLink(
    modname=modname,
    filename='static/ie.css',
    media='screen, projection')

##
## Blueprint Plugins
##

# Gives you some great CSS-only buttons.
tw2_blueprint_plugin_buttons_css = twc.CSSLink(
    modname=modname,
    filename='static/plugins/buttons/screen.css')

# Gives you classes to use if you'd like some extra fancy typography.
tw2_blueprint_plugin_fancytype_css = twc.CSSLink(
    modname=modname,
    filename='static/plugins/fancy-type/screen.css')

# Icons for links based on protocol or file type.
tw2_blueprint_plugin_linkicons_css = twc.CSSLink(
    modname=modname,
    filename='static/plugins/link-icons/screen.css',
    media='screen, projection')

# Mirrors Blueprint, so it can be used with Right-to-Left languages.
tw2_blueprint_plugin_rtl_css = twc.CSSLink(
    modname=modname,
    filename='static/plugins/rtl/screen.css',
    media='screen, projection')

# Blueprint Silk Sprite
# * Silk Sprite is Based on the Silk Icon Set by Mark James [famfamfam.com]
# * Compiled & Adapted for Blueprint by Don Albrecht [ajaxbestiary.com]
# * Usage released under a creative commons Attribution 2.5 license
#   http://creativecommons.org/licenses/by/2.5/
tw2_blueprint_sprites_css = twc.CSSLink(
    modname=modname,
    filename='static/plugins/sprites/sprite.css',
    media='screen')


if asbool(config.get('moksha.use_tw2', False)):
    blueprint_screen_css = tw2_blueprint_screen_css
    blueprint_print_css = tw2_blueprint_print_css
    blueprint_ie_css = tw2_blueprint_ie_css

    blueprint_plugin_buttons_css = tw2_blueprint_plugin_buttons_css
    blueprint_plugin_fancytype_css = tw2_blueprint_plugin_fancytype_css
    blueprint_plugin_linkicons_css = tw2_blueprint_plugin_linkicons_css
    blueprint_plugin_rtl_css = tw2_blueprint_plugin_rtl_css
    blueprint_sprites_css = tw2_blueprint_sprites_css
else:
    blueprint_screen_css = tw1_blueprint_screen_css
    blueprint_print_css = tw1_blueprint_print_css
    blueprint_ie_css = tw1_blueprint_ie_css

    blueprint_plugin_buttons_css = tw1_blueprint_plugin_buttons_css
    blueprint_plugin_fancytype_css = tw1_blueprint_plugin_fancytype_css
    blueprint_plugin_linkicons_css = tw1_blueprint_plugin_linkicons_css
    blueprint_plugin_rtl_css = tw1_blueprint_plugin_rtl_css
    blueprint_sprites_css = tw1_blueprint_sprites_css

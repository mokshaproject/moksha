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

"""
:mod:`moksha.widgets.jquery_ui_theme` - jQuery UI Theme
=======================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from paste.deploy.converters import asbool

import tw.api

tw1_ui_theme_css = tw.api.CSSLink(
    link='/css/jquery-ui/ui.theme.css', modname=__name__)
tw1_ui_base_css = tw.api.CSSLink(
    link='/css/jquery-ui/ui.base.css',
    css=[tw1_ui_theme_css],
    modname=__name__)

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    ui_theme_css = tw1_ui_theme_css
    ui_base_css = tw1_ui_base_css


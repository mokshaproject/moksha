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
:mod:`moksha.wsgi.widgets.iframe` - An IFrame Widget
===============================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import tw2.core as twc

# TODO -- this should be removed and replaced with
#         http://tw2-demos.threebean.org/module?module=tw2.etc


class IFrameWidget(twc.Widget):
    params = ['id', 'url', 'title', 'height', 'width']
    template = "mako:moksha.wsgi.widgets.templates.iframe"
    title = ''
    height = width = '100%'


iframe_widget = IFrameWidget(id='iframe_widget')

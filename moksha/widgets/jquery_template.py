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

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

tw1_jquery_template_js = tw.api.JSLink(
    modname=__name__,
    filename='static/jquery.tmpl.js',
    javascript=[tw.jquery.jquery_js])

tw2_jquery_template_js = twc.JSLink(
    modname=__name__,
    filename='static/jquery.tmpl.js',
    resources=[tw2.jquery.jquery_js])

if asbool(config.get('moksha.use_tw2', False)):
    jquery_template_js = tw2_jquery_template_js
else:
    jquery_template_js = tw1_jquery_template_js

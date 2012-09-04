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

import tw2.core as twc

from moksha.wsgi.widgets.container import MokshaContainer


# set up the middleware for the tests
def request_local_tst():
    global _request_local, _request_id
    #    if _request_id is None:
    #        raise KeyError('must be in a request')
    if _request_local == None:
        _request_local = {}
    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

twc.core.request_local = request_local_tst
_request_local = {}
_request_id = 'whatever'


class TestContainer:

    def setUp(self):
        twc.core.request_local = request_local_tst
        twc.core.request_local()['middleware'] = twc.make_middleware()
        self.w = MokshaContainer(id='test')

    def test_render_widget(self):
        assert 'Moksha Container' in self.w.display()

    def test_widget_content(self):
        """ Ensure we can render a container with another widget """

        class MyWidget(twc.Widget):
            template = "mako:moksha.wsgi.widgets.container.tests.templates.w"

        assert 'Hello World!' in self.w.display(
            content=MyWidget(id='mywidget'))

    def test_container_classes(self):
        rendered = self.w.display(**dict(skin3=True, stikynote=True,
                                         draggable=True, resizable=True))
        assert(
            'class="containerPlus draggable resizable"' in rendered,
            rendered
        )

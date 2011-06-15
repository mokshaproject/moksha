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

from tw.api import Widget
from moksha.widgets.container import MokshaContainer

class TestContainer:

    def setUp(self):
        self.w = MokshaContainer('test')

    def test_render_widget(self):
        assert 'Moksha Container' in self.w()


    def test_widget_content(self):
        """ Ensure we can render a container with another widget """

        # TODO -- test this for both tw1 and tw2?
        class MyWidget(Widget):
            template = """
                Hello World!
            """
        assert 'Hello World!' in self.w(content=MyWidget('mywidget'))

    def test_container_classes(self):
        rendered = self.w(**dict(skin3=True, stikynote=True,
                                 draggable=True, resizable=True))
        assert 'class="containerPlus draggable resizable"' in rendered, rendered

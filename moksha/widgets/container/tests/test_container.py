from tw.api import Widget
from moksha.widgets.container import JQueryMbContainer

class TestContainer:

    def setUp(self):
        self.w = JQueryMbContainer('test')

    def test_render_widget(self):
        assert '<div id="test" ' in self.w()

    def test_widget_content(self):
        """ Ensure we can render a container with another widget """
        class MyWidget(Widget):
            template = 'Hello World!'
        assert 'Hello World!' in self.w(content=MyWidget('mywidget'))

    def test_container_classes(self):
        assert 'class="container skin3 stikynote draggable resizable"'\
                in self.w(**dict(skin3=True, stikynote=True,
                                 draggable=True, resizable=True))
        assert 'class="container"' \
                in self.w(**dict(skin3=True, stikynote=True,
                                 draggable=True, resizable=True))

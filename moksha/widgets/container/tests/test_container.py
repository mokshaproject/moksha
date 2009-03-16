from tw.api import Widget
from moksha.widgets.container import MokshaContainer

class TestContainer:

    def setUp(self):
        self.w = MokshaContainer('test')

    def test_render_widget(self):
        assert '<div id="test" ' in self.w()

    def test_widget_content(self):
        """ Ensure we can render a container with another widget """
        class MyWidget(Widget):
            template = """
                Hello World!
            """
        assert 'Hello World!' in self.w(content=MyWidget('mywidget'))

    def test_container_classes(self):
        rendered = self.w(**dict(skin3=True, stikynote=True,
                                 draggable=True, resizable=True))
        assert 'class="containerPlus draggable resizable"' in rendered, rendered

from tw.api import Widget
from widgetbrowser import WidgetBrowser
from formencode.api import Invalid

class TestWidget(Widget):
    template = "$value"
    default = "default"

    def validate(self, value, *args, **kw):
        if 'break' in value.keys():
            raise Invalid("Validation failed", value, None)
        return value

@WidgetBrowser.register_controller(TestWidget, 'test')
def test_controller(request, response):
    response.headers['Content-Type'] = 'text/plain'
    return "Testing " + request.widget.__class__.__name__

class TestWidgetExternalTemplate(Widget):
    template = "toscawidgets:widgetbrowser.tests.dummy_template"
    default = "default"

class TestWidgetMultipleExternalTemplate(Widget):
    template = "toscawidgets:widgetbrowser.tests.dummy_m_template"
    default = "default"

from tw.api import WidgetList, Widget

class MyWidgetViews(Widget):
    class views(WidgetList):
        mobi = MyMobileWidget
        sidebar = MySidebarWidget
        content = MyContentWidget


class MyBaseWidget(Widget):
    views = MyWidgetViews
    views = {'mobi': MyMobileWidget, 'sidebar': MySidebarWidget}

class MyMobileWidget(MyBaseWidget):
    template = 'mymobiletemplate'



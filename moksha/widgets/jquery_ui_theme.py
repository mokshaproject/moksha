from tw.api import Widget, CSSLink

class JQueryUITheme(Widget):
    css = [CSSLink(link='/css/jquery-ui/ui.theme.css', modname=__name__)]
    template = ''

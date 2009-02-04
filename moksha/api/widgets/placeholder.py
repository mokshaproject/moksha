from tw.api import Widget

class Placeholder(Widget):
    engine_name = 'mako'
    template = """
<div class='placeholder'>
    Moksha application <strong>${appname}</strong> is not registered yet.  This is a placeholder
    for testing purposes.  When the app is registered it will appear in the
    layout once the server is restarted.
</div>
"""

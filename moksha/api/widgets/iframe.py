from tw.api import Widget

class IFrameWidget(Widget):
    params = ['id', 'url']
    template = """
      <iframe id="${id}" src="${url}" width="100%" height="100%">
        <p>Your browser does not support iframes.</p>
      </iframe>
    """
    engine_name = 'mako'

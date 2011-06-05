
lol = None # lolwhut?
try:
    import fabulous.color as lol
except ImportError as e:
    pass

def _color(col, s):
    return getattr(lol, col, lambda _s:_s)(s)

def cyan(s):
    return _color('cyan', s)

def red(s):
    return _color('red', s)

def green(s):
    return _color('green', s)

def yellow(s):
    return _color('yellow', s)

def magenta(s):
    return _color('magenta', s)

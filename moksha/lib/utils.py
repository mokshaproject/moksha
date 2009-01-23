from decorator import decorator

@decorator
def trace(f, *args, **kw):
    r = f(*args, **kw)
    print "%s(%s, %s) = %s" % (f.func_name, args, kw, r)
    return r

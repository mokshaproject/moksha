""" Mako utilities for tw1/tw2 backwards compatibility.

TODO -- eventually phase this out and use tw2.core.mako_util:compat
"""

def compat(context, attr):
    """ Backwards compatible widget attribute access.

    In tw1, all template attributes looked like:
        ${some_attribute}

    Whereas in tw2 they look like:
        ${w.some_attribute}

    This is a *nuisance* if you want to reuse a template between tw1 and tw2
    widgets.  With this function you can write:
        <%namespace name="tw" module="moksha.utils.mako"/>
        ${tw.compat(attr='some_attribute')}
    or
        ${tw._('some_attribute')}

    Nice, right? :)
    """

    if not 'w' in context.keys():
        # Must be tw1
        return context.get(attr)
    else:
        # Must be tw2
        return getattr(context.get('w'), attr)

_ = compat  # Just for shorthand

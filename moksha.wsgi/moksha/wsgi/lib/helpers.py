from tw2.core import js_callback


def when_ready(func):
    """
    Takes a js_function and returns a js_callback that will run
    when the document is ready.

        >>> from tw.api import js_function
        >>> print when_ready(js_function('jQuery')('foo').bar({'biz': 'baz'}))
        $(document).ready(function(){jQuery("foo").bar({"biz": "baz"})});
    """
    from tw2.core import js_callback
    return js_callback('$(document).ready(function(){' + str(func) + '});')

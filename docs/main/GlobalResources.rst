=========================
Global Resource Injection
=========================

Moksha has plugin suport for `Global Resources`, which are just JavaScript or
CSS widgets that will get automatically injected in every page by the
:class:`GlobalResourceInjectionWidget`.

Moksha will load all `tw2.core.JSLink`, `tw2.core.CSSLink`, and
`tw2.core.Widget` ToscaWidgets that are on the `[moksha.global]`
entry-point.

Installing a Global Resource Widget
-----------------------------------

By default Moksha includes only its live socket widget as a global resource.
Developers often want to include other resources like jQuery or jQuery UI.
Here is an example of what that might look like in your `setup.py` entry-points:

.. code-block:: python

    [moksha.global]

    jquery = tw2.jquery:jquery_js
    jquery_ui = tw2.jqplugins.ui:jquery_ui

LiveWidget dependency on moksha_socket
--------------------------------------

As mentioned, :class:`GlobalResourceInjectionWidget` is also responsible for
rendering the moksha_socket which creates the callbacks for any :class:`LiveWidget`
being rendered.  Because of the way this works, you should ensure the
:class:`GlobalResourceInjectionWidget` is injected *last*, after each LiveWidget
has been rendered.

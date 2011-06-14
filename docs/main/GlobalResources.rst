=========================
Global Resource Injection
=========================

Moksha has plugin suport for `Global Resources`, which are just JavaScript or
CSS widgets that will get automatically injected in every page by the
:class:`GlobalResourceInjectionWidget`.

Moksha will load all `JSLink
<http://toscawidgets.org/documentation/ToscaWidgets/modules/api.html#jslink>`_,
`CSSLink
<http://toscawidgets.org/documentation/ToscaWidgets/modules/api.html#csslink>`_,
and `Widget` ToscaWidgets that are on the `[moksha.global]` entry-point.  You can point to
classes, or instantiated objects.

Installing a Global Resource Widget
-----------------------------------

By default Moksha includes global resources for jQuery, jQuery UI, and the Blueprint CSS framework.
Here is an example of what some global resources look like in Moksha's `setup.py` entry-points.

.. code-block:: python

    [moksha.global]

    jquery = tw.jquery:jquery_js
    jquery_ui_core = tw.jquery.ui:ui_core_js
    jquery_ui_draggable = tw.jquery.ui:ui_draggable_min_js
    jquery_ui_resizable = tw.jquery.ui:ui_resizable_min_js
    jquery_ui_dialog = tw.jquery.ui:ui_dialog_min_js
    jquery_ui_tabs = tw.jquery.ui_tabs:jquery_ui_tabs_js

    # Enable support for the Blueprint CSS framework & Plugins
    blueprint_ie_css = moksha.widgets.blueprint:blueprint_ie_css
    blueprint_screen_css = moksha.widgets.blueprint:blueprint_screen_css
    blueprint_print_css = moksha.widgets.blueprint:blueprint_print_css
    blueprint_fancytype_css = moksha.widgets.blueprint:blueprint_plugin_fancytype_css

LiveWidget dependency on moksha_socket
--------------------------------------

The :class:`GlobalResourceInjectionWidget` is also responsible for rendering the moksha_socket which
creates the callbacks for any :class:`LiveWidget` being rendered.  Because of the way this works,
you should ensure the :class:`GlobalResourceInjectionWidget` is injected *last*, after each
LiveWidget has been rendered.

=========
Blueprint
=========

"`Blueprint <http://blueprintcss.org>`_ is a CSS framework, which aims to cut
down on your development time.  It gives you a solid foundation to build your
project on top of, with an easy-to-use grid, sensible typography, useful
plugins, and even a stylesheet for printing."

Moksha comes with `Blueprint <http://www.blueprintcss.org>`_ support out of the
box.  To enable blueprint, and various plugins, in your application, simply add
it to your apps entry-points.

.. code-block:: python

   [moksha.global]

   blueprint_ie_css = moksha.widgets.blueprint:blueprint_ie_css
   blueprint_screen_css = moksha.widgets.blueprint:blueprint_screen_css
   blueprint_print_css = moksha.widgets.blueprint:blueprint_print_css

   ## Moksha comes with various Blueprint plugins as well

   # Gives you classes to use if you'd like some extra fancy typography.
   blueprint_fancytype_css = moksha.widgets.blueprint:blueprint_plugin_fancytype_css

   # Gives you some great pure-CSS buttons.
   blueprint_plugin_buttons_css = moksha.widgets.blueprint:blueprint_plugin_buttons_css

   # Icons for links based on protocol or file type.
   blueprint_plugin_linkicons_css = moksha.widgets.blueprint:blueprint_plugin_linkicons_css

   # Mirrors Blueprint, so it can be used with Right-to-Left languages.
   blueprint_plugin_rtl_css = moksha.widgets.blueprint:blueprint_plugin_rtl_css

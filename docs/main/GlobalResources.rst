=========================
Global Resource Injection
=========================

Moksha has plugin suport for `Global Resources`, which are just JavaScript or
CSS widgets that will get automatically injected in every page by the
:class:`GlobalResourceInjectionWidget`

Moksha will load all `JSLink
<http://toscawidgets.org/documentation/ToscaWidgets/modules/api.html#jslink>`_
and `CSSLink
<http://toscawidgets.org/documentation/ToscaWidgets/modules/api.html#csslink>`_
ToscaWidgets that are on the `[moksha.global]` entry-point.  You can point to
classes, or instantiated objects.

Installing a Global Resource Widget
-----------------------------------

For example, to add jQuery to every page, you would add the following to your application's setuptools entry-points:

.. code-block:: python

    [moksha.global]
    jquery = tw.jquery:jquery_js

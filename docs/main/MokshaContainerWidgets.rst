Moksha Container Widgets
========================

Moksha container widgets provide configurable containers for loading Moksha
applications and widgets.  They are used for layout, navigation and dynamic
loading of content on your site.  The configuration format for specifying
components to load into containers make it easy to dynamically store and update
configuration information including location and default settings of an
application.  Containers can load applications asynchronously through JavaScript
or pull in a widget during the initial request.  Since containers are widgets
themselves containers can be nested.

Configuration Format
--------------------

Configuration for each container is done using a restricted python syntax and
can be passed to the container as a string or a Python object.  Strings are
mainly used when reading from a configuration file but can also be used to avoid
having to import the configuration wrapper objects.

Here is an example of what a configuration line could look like:

.. code-block:: python

    dashboard_layout =
        [Category('Test Applications', [
                    MokshaApp('Hello World 1',
                              'moksha.helloworld',
                              {'name':'J5'}),
                    App('Hello World 2',
                              '/apps/moksha.helloworld',
                              {'name':'Luke'}),
                    MokshaWidget('Hello World 3',
                              'moksha.helloworldwidget',
                              {'name':'Anonymous'}, auth=Not(not_anonymous()))
                                        ]
                  )
         ]

This would be a configuration for the dashboard container discussed bellow.
It defines one category, two applications and a widget.  How this is laid out
in your final view is up to the template and css.  The default view is setup
to load each component into it's category div in order.  You can then specify
CSS to position those categories in your layout.

Lets look at each individual component.

* Category 'Test Applications' - This tells the container that you want to group
  a number of applications under the 'Test Application' title which in essence
  creates a div with class 'test_applications'.  You may also want to specify
  css_class instead of relying on the label.

* MokshaApp 'Hello World 1': here we dynamically load the moksha application
  installed on the ``moksha.application`` entry point as ``moksha.helloworld``.
  We then send it a dictionary of keys - in this case the key 'name'.

* App 'Hello World 2': This is the same as the above but instead of giving
  the application name we give it the url the application is mounted on.  We
  also send in different configuration data. The App object allows for non
  moksha web apps and static content to be placed in a container.

* MokshaWidget 'Hello World 3': Again this is the same as above but we pass in
  a widget installed on the ``moksha.widget`` entry point as
  ``moksha.helloworldwidget``.  We also pass in a auth predicate.  If the
  authorization evaluates to True, in this case if the user is anonymous, the
  widget will be embedded in the page.  If not then it is removed.  Predicates
  are defined by the :module:`repoze.what.authorize` module and can be added to
  any ConfigWrapper.

Tabbed Container
----------------

:class:`moksha.api.widgets.containers.TabbedContainer`

A tabbed container is a container that places components in a jQuery.ui.tabs
javascript widget.  Applications are then dynamically loaded when that tab is
selected.  Widgets placed in a tabbed container are continuously running while
the tabbed container is active even if not visible.  It is important to not load
widgets that have a high resource requirement.  Tabbed containers must be
subclassed in order to point it to the correct resources.

Here is an example on how to subclass a TabbedContainer:

mainnav.py

.. code-block:: python

    from moksha.api.widgets.containers import TabbedContainer

    class MainNav(TabbedContainer):
        template = 'mako:myapp.templates.mainnav'
        config_key = 'myapp.mainnav.apps'

mainnav.mak

.. code-block:: html

    <div>
      <ul id="${id}">
        % for t in tabs:
          <li>
            % if t.has_key('url'):
              <a href="${t['url']}" title="${t['label']} Page">
                ${t['label']}
              </a>
            % else
              ${t['label']}
            % endif
          </li>
        % endfor
      </ul>
    </div>
    <div id="content">
      % for t in tabs:
        <div id="${t['label']}_Page">
          % if t.has_key('widget'):
            ${t['widget'](t['params'])}
          % endif
        </div>
      % endfor
    </div>

development.ini

.. code-block:: python

    [DEFAULT]
    myapp.mainnav.apps = (MokshaApp('Home', 'myapp.home'),
                          MokshaApp('2nd Tab', 'myapp.tab2'),
                          MokshaApp('3rd Tab','myapp.tab3',
                                    auth=not_anonymous()),
                          MokshaApp('4th Tab', 'myapp.tab4',
                                    auth=Not(not_anonymous())
                                   )
                         )

It should be noted that the template boilerplate should be handled automatically
in the future.

Dashboard Container
-------------------

:class:`moksha.api.widgets.containers.DashboardContainer`

A dashboard container is a container that places components in a
jQuery.ui.sortable javascript widget.  Applications are dynamically loaded in
the order they are placed in the configuration.  Dashboard containers must be
subclassed in order to point it to the correct resources.

Here is an example on how to subclass a DashboardContainer:

homepage.py

.. code-block:: python

    from moksha.api.widgets.containers import DashboardContainer

    class HomePageContainer(DashboardContainer):
        template = 'mako:myapp.templates.homepagecontainer'
        layout = [Category('left-content-column',
                           [App('Banner', '/static-html/sitebanner.html'),
                            MokshaApp('Stable Updates','myapp.updates/table',
                                      {"some_json":'{"status":"stable"}'}
                                     ),
                            MokshaApp('Testing Updates','myapp.updates/table',
                                      {"some_json":'{"status":"testing"}'}
                                     ),
                            ]),
                  Category('right-content-column',
                           MokshaWidget(None, 'myapp.loginwidget',
                                        auth=Not(not_anonymous())
                                       )
                          )
                 ]

homepagecontainer.mak

.. code-block:: html

  <div id="${id}">
    <div>
      <div id="right-content-column">
        ${applist_widget(category = 'right-content-column', layout = layout)}
      </div>
      <div id="left-content-column">
        ${applist_widget(category = 'left-content-column', layout = layout)}
      </div>
    </div>
  </div>

Notice above that I decided to use the layout calls variable instead of a
configuration key.  Either form is acceptable for any container.

Issues
------

Moving from a model where you piece everything together on the server to
dynamically loading content in the browser means that there are some issues
to consider.

* Id's may clash.  It is suggested that when using jQuery
  or any other javascript dom tool to generate a uuid and do all of your
  selections relative to that id. It is also suggested you namespace your id's
  and only use classes to style.

* Javascript may load more than once.  If all you uses is widgets you are fine
  as ToscaWidgets will take care of duplicate resource requests.  However a
  powerful concept in moksha is the ability to load applications asynchronously
  so that the user does not have to wait for the server to finish processing a
  page before any data is streamed to them.  It is suggested you make heavy use
  of global resources in order to aleviate the issue.  At some point we may
  introduce a way for the browser to filter out already loaded javascript and
  other resources.

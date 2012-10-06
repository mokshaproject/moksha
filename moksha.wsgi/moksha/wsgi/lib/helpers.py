
from repoze.what.authorize import check_authorization, NotAuthorizedError
from repoze.what.predicates import  (Not, Predicate, All, Any,
                                     has_all_permissions, has_any_permission,
                                     has_permission, in_all_groups,
                                     in_any_group, in_group, is_user,
                                     not_anonymous)
from webob import Request
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


def _update_params(params, d):
    p = {}
    if params:
        for k in params.iterkeys():

            if d and (k in d):
                value = d[k]
            else:
                value = params[k]

            # recursive dicts also get updated
            # by the passed params
            if isinstance(value, dict):
                value = _update_params(value, d)
                value = json.encode(value)
            elif isinstance(value, list):
                value = value

            if value != None:
                p[k] = value

    return p


class ConfigWrapper(object):
    """ Base class for container configuration wrappers

    Configuration Wrappers are python objects which can be embedded in
    configuration stores (files and databases) or used directly to
    insert web applications into containers.  Wrappers also integrate
    repoze.what predicates which are checked when the wrapper is processed.
    If the prediates return False the web application is not displayed to
    the user.  This makes it easy to build composite Moksha applications
    where what the user is show is dictated by their authorization level.

    Configuration wrapper are only standard data structures with the ability
    to process predicates.  A container widget is needed to convert the
    configuration into rendered applications on a page.

    Derive from this class to create new configuration syntax

    """

    def _update_nested_dicts(self, dest, source):
        """Recursive helper which updates nested dicts"""

        for key, value in source.iteritems():
            if key in dest:
                if isinstance(dest[key], dict):
                    self._update_nested_dicts(dest[key], value)
                else:
                    dest[key] = value
            else:
                dest[key] = value

    @staticmethod
    def _validate_predicates(predicates):
        if not isinstance(predicates, (list, tuple)):
            predicates = (predicates,)

        for p in predicates:
            if not isinstance(p, Predicate):
                raise AttributeError('"%r" is not a subclass of repoze.who.predicates.Predicate' % p)

    @staticmethod
    def process_wrappers(wrappers, d):
        """ Helper method for evlauating a list of wrappers

        :returns: a list of hashes for each of the application
                  that will be displayed
        """

        result = []
        if isinstance(wrappers, ConfigWrapper):
            w = wrappers.process(d)
            if w:
                result.append(w)
        else:
            for item in wrappers:
                w = item.process(d)
                if w:
                    result.append(w)

        return result

    def process(self, d=None):
        """Override this in derived classes to update the hash representing
        the configuration option
        """
        default_values = dict(query_string='',
                              id='uuid' + str(uuid.uuid4()),
                              type=self.__class__.__name__)

        return default_values

class Category(ConfigWrapper):
    """A configuration wrapper class that displays a list of application
    and/or widget wrappers

    :Example:
        left_column = Category("Left Column Apps",
                               [App(...), App(...)],
                               not_anonymous())
    """

    def __init__(self, label="", apps=None, css_class=None, auth=None,
                default_child_css=None):
        """
        :label: The category heading the container should use when rendering
                a category.  Labels for categories are not rendered in the
                default template. If a css_class is not defined the label
                becomes the css class for the div once it has been scrubbed
                by making it all lower case and replacing illegal characters
                with underscores.
        :apps: A list of wrappers representing application configurations
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this category
        :default_child_css: Either a string or list of strings defining the
                            default css for child apps and widgets
        """
        super(Category, self).__init__()

        self.label = label
        self.apps = apps or tuple()
        if not isinstance(self.apps, tuple):
            if not getattr(self.apps, '__iter__', False):
                self.apps = (self.apps,)
            else:
                self.apps = tuple(self.apps)
        self.auth = auth or tuple()

        self._validate_predicates(self.auth)

        if not css_class:
            css_class = scrub_filter.sub('_', self.label.lower())
        elif isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)

        self.css_class = css_class

        if isinstance(default_child_css, list) or isinstance(css_class, tuple):
            default_child_css = ' '.join(default_child_css)

        for a in self.apps:
            a.set_default_css(default_child_css)

    def process(self, d=None):
        """Check the predicates and construct the dict

        :returns: a dict with all the configuration data for this category
        """
        results = super(Category, self).process(d)

        if not check_predicates(self.auth):
            return None

        apps = self.process_wrappers(self.apps, d)
        results.update({'label': self.label,
                  'apps': apps,
                  'css_class': self.css_class})

        return results

class App(ConfigWrapper):
    """A configuration wrapper class that displays an application pointed to
    by a url

    :Example:
        hello_app = App('Hello World App',
                        '/apps/moksha.helloworld',
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())
    """
    def __init__(self, label="", url="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the application should use when rendering
                in a container.  Leave this blank if you do not wish the
                application to be visibly labeled when rendered
        :url: the url to load this application from
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of request parameters to send to the application
                 when loading it from a url
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        super(App, self).__init__()

        self.label = label
        self.url = url
        self.params = params or {}
        self.auth = auth or []
        self.content_id = content_id

        self._validate_predicates(self.auth)

        if isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)
        self.css_class = css_class

        if self.label and not self.content_id:
            self.content_id = scrub_filter.sub('_', self.label.lower())

    def clone(self, update_params=None, auth=None, content_id=None, label=None):
        if not update_params:
            update_params = {}

        params = copy.deepcopy(self.params)

        self._update_nested_dicts(params, update_params)

        if auth == None:
            auth = self.auth

        if content_id == None:
            content_id == self.content_id

        if label == None:
            label = self.label

        return App(label=label,
                   url=self.url,
                   params=params,
                   auth=auth,
                   content_id=content_id,
                   css_class=self.css_class)

    def set_default_css(self, css):
        """ If we already have css defined ignore, otherwise set our css_class
        """
        if(self.css_class == None):
            self.css_class = css

    def _create_query_string(self, params):
        qlist = []
        for k, i in params.iteritems():
            if isinstance(i, (list, tuple)):
                # break out lists into multiple entries of the same key
                for j in i:
                    s = str(j)
                    s = urllib.quote_plus(s)
                    qlist.append("%s=%s" % (k, s))

            else:
                s = str(i)
                s = urllib.quote_plus(s)

                qlist.append("%s=%s" % (k, s))

        result = ""
        if qlist:
            result = '?' + '&'.join(qlist)

        return result

    def process(self, d=None):
        """Check the predicates and construct the dict

        :returns: a dict with all the configuration data for this application
        """
        if not check_predicates(self.auth):
            return None

        results = super(App, self).process(d)

        css_class = self.css_class
        if css_class == None:
            css_class = ''

        p = _update_params(self.params, d)
        qs = self._create_query_string(p)
        results.update({'label': self.label, 'url': self.url,
                'params': p,
                'json_params': json.encode(p),
                'query_string': qs,
                'content_id': self.content_id + '-' + results['id'],
                'css_class': css_class})

        return results

class StaticLink(App):
    """A configuration wrapper class that shows up as a static link in nav
    elements"""

class MokshaApp(App):
    """A configuration wrapper class that displays a Moksa application
    selected by name. This differes from App in that you don't have to
    know the url, only the name the application is mounted under.  In
    future versions we may also try and get the auth predicated from
    the application's own configuration.

    :Example:
        hello_app = App('Hello World Moksha App',
                        'moksha.helloworld',
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())

    """
    def __init__(self, label="", moksha_app="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the application should use when rendering
                in a container.  Leave this blank if you do not wish the
                application to be visibly labeled when rendered
        :moksha_app: the name of the entry point registered under the
                     moksha.application section
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of request parameters to send to the application
                 when loading it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        # FIXME figure out how to pull auth info from an app
        app = moksha_app.split('/')[0]
        self.app = app
        super(MokshaApp, self).__init__(label,
                                        '/apps/' + moksha_app,
                                        content_id,
                                        params, auth, css_class)

    def process(self, d=None):
        # We return a placeholder if the app is not registered
        if not moksha._apps.has_key(self.app):
            return MokshaWidget(self.label, 'placeholder',
                                self.content_id,
                                {'appname':self.app},
                                self.auth,
                                self.css_class).process(d)
        else:
            results = super(MokshaApp, self).process(d)
            return results

class Widget(ConfigWrapper):
    """A configuration wrapper class that displays a ToscaWidget.  Use this
    instead of an App when the time it takes to load an application from a url
    is more than the time it takes to just embed it in the template.  Widgets
    also lack the ability to respond to remote requests via controllers.

    :Example:
        class HelloWidget(tw.api.Widget):
            pass

        hello_widget = Widget('Hello World Widget',
                        HelloWidget(),
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())

    """
    def __init__(self, label="", widget=None, content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the widget should use when rendering
                in a container.  Leave this blank if you do not wish the
                widget to be visibly labeled when rendered
        :widget: the ToscaWidget to be rendered
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of parameters to send to the widgets update_params
                 method when rendering it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        super(Widget, self).__init__()
        self.label = label
        self.widget = widget
        self.params = params or {}
        self.auth = auth or []
        self._validate_predicates(self.auth)

        self.content_id = content_id

        if isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)
        self.css_class = css_class

        if self.label and not content_id:
            self.content_id = scrub_filter.sub('_', self.label.lower())

    def clone(self, update_params=None, auth=None, content_id=None):
        if not update_params:
            update_params = {}
        params = copy.deepcopy(self.params)
        self._update_nested_dicts(params, update_params)

        if auth == None:
            auth = self.auth;

        if content_id == None:
            content_id = self.content_id

        return Widget(label=self.label,
                   widget=self.widget,
                   params=params,
                   auth=auth,
                   content_id=content_id,
                   css_class=self.css_class)

    def set_default_css(self, css):
        """ If we already have css defined ignore, otherwise set our css_class
        """
        if(self.css_class == None):
            self.css_class = css

    def process(self, d=None):
        if not check_predicates(self.auth):
            return None

        results = super(Widget, self).process(d)

        content_id = self.content_id + '-' + results['id']
        url = '#' + content_id
        results.update({'label': self.label, 'url': url,'widget': self.widget ,
                'params':_update_params(self.params, d), 'id': results['id'],
                'content_id': content_id, 'css_class': self.css_class})

        return results

class MokshaWidget(Widget):
    """A configuration wrapper class that displays a ToscaWidget registered
    in Moksha's widget dictionary.

    :Example:
        hello_moksha_widget = Widget('Hello Moksha Widget',
                                     'moksha.hello',
                                     params={'greeter_name': 'J5'},
                                     auth=not_anonymous())

    """
    def __init__(self, label="", moksha_widget="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the widget should use when rendering
                in a container.  Leave this blank if you do not wish the
                widget to be visibly labeled when rendered
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :moksha_widget: the name of the entry point registered under the
                        moksha.widget section
        :params: A dict of parameters to send to the widgets update_params
                 method when rendering it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        widget = moksha.utils._widgets[moksha_widget]['widget']
        return super(MokshaWidget, self).__init__(label=label, widget=widget,
                                           content_id=content_id, params=params,
                                           auth=auth,
                                           css_class=css_class)

class param_contains(Predicate):
    """
    Checks the parameters of the environment and return True if the
    parameter contains the value specified.  If the parameter is a list
    (more than one value) then check each item in the list.
    Note this is the environment params (query string and post file) not the TG
    or ToscaWidget param dicts
    """
    message = u'Parameter "%(param)s" is does not contain value "%(value)s"'

    def __init__(self, param, value, **kwargs):
        super(param_contains, self).__init__(**kwargs)
        self.param = param
        self.value = value

    def evaluate(self, environ, credentials):
        req = Request(environ)
        p = req.params.getall(self.param)

        if not p:
            return self.unmet(param = self.param, value = self.value)

        print p
        for v in p:
            print v, '==', self.value
            if v == self.value:
                return

        return self.unmet(param = self.param, value = self.value)

class param_has_value(Predicate):
    """
    Checks the parameters of the environment and return True if the
    parameter specified holds a value.  Note this is the environment params
    (query string and post file) not the TG or ToscaWidget param dicts
    """
    message = u'Parameter "%(param)s" is not set'

    def __init__(self, param, empty_str_is_valid = False, **kwargs):
        super(param_has_value, self).__init__(**kwargs)
        self.param = param
        self.empty_str_is_valid = empty_str_is_valid

    def evaluate(self, environ, credentials):
        req = Request(environ)
        p = req.params.getall(self.param)

        if not p:
            return self.unmet(param = self.param)

        p = p[0]
        if p == None:
            return self.unmet(param = self.param)

        if not self.empty_str_is_valid and p == '':
            return self.unmet(param = self.param)

        return

# setup the dictionary of acceptable callables when eval'ing predicates from
# a configuration file - this makes up the keywords of the predicate
# configuration format
_safe_predicate_callables = {
                    'Not': Not,
                    'All': All,
                    'Any': Any,
                    'param_has_value': param_has_value,
                    'has_all_permissions': has_all_permissions,
                    'has_any_permission': has_any_permission,
                    'has_permission': has_permission,
                    'in_all_groups': in_all_groups,
                    'in_any_group': in_any_group,
                    'in_group': in_group,
                    'is_user': is_user,
                    'not_anonymous': not_anonymous}

# setup the dictionary of acceptable callables when eval'ing config wrappers
# from a configuration file - this makes up the keywords of the config wrapper
# configuration format
_app_config_callables = {'Category': Category,
                         'MokshaApp': MokshaApp,
                         'Widget': Widget,
                         'App': App,
                         'MokshaWidget': MokshaWidget}

# config wrapper configuration can also utilize predicates
_app_config_callables.update(_safe_predicate_callables)


def eval_app_config(config_str):
    """
    Safely evaluates application configuration strings for storing application
    layout data in a moksha configuration file

    :return: the evaluated configuration wrapper configuration
    """
    return eval(config_str, {"__builtins__":None}, _app_config_callables)


def eval_predicates(predicate_str):
    """
    Safely evaluates a string of predicates

    :return: the evaluated predicate configuration
    """
    return eval(predicate_str, {"__builtins__":None}, _safe_predicate_callables)


def check_predicates(predicates):
    """
    Using the current WSGI environment run a list of predicates.
    This can only be used when inside a WSGI request

    :return: False is any one is False
    :return: True if they are all True
    """
    from pylons import request

    if(not(isinstance(predicates, list) or isinstance(predicates, tuple))):
        predicates = (predicates,)

    for p in predicates:
        try:
            check_authorization(p, request.environ)
        except NotAuthorizedError, e:
            return False

    return True

def eval_and_check_predicates(predicate_str):
    """
    Using the current WSGI environment evaluate a predicate sting and run
    the resulting predicate list. This can only be used when inside a WSGI
    request

    :return: False is any one is False
    :return: True if they are all True
    """
    p = eval_predicates(predicate_str)
    return check_predicates(p)



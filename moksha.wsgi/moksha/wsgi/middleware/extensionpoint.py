# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: John (J5) Palmieri <johnp@redhat.com>

import logging
import pkg_resources

from webob import Request, Response

from moksha.common.exc import ApplicationNotFound, MokshaException

log = logging.getLogger(__name__)

import shlex
import os

class Chunk(object):
    def __init__(self):
        self.consumes = []
        self.info = ""
        self.code = ""

    def parse_consumes_field(self):
        start = self.info.find('consumes') + 8
        start = self.info.find('[',start)
        end = self.info.find(']', start)

        consumes = self.info[start + 1 : end]

        self.consumes = shlex.split(consumes)

class MokshaExtensionPointMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for serving
    javascript extensions.

    If a request for an extension comes in (/moksha_extension/$extension_point),
    it will serve up any extensions that consume the extension point.

    This works by searching for all extensions of a given type and creating a
    javascript array pointing to their run functions.

    All extensions should contain at least a run function which will be passed
    the data fields specified by the extension point.  They should also return
    the HTML they wish to be embedded at the extension point. e.g.:

    function run(data) {
      // data will always contain a uid field and the HTML you return
      // will be wrapped in a div with that id
      return "<div>Hello</div>";
    };

    Extensions also need a header which describes the extension as such:

    info : {'consumes':['build_message'],
            'author': 'John (J5) Palmieri <johnp@redhat.com>',
            'version': '0.1',
            'name': 'Hello World Message'}

    """
    def __init__(self,
                 application,
                 config,
                 entry_point='moksha.extension_point',
                 test_dir=None):
        """
        :application: WSGI application to wrap
        :config: a dict of config values
        :extension_point: the python extry point which specifies modules to
                          scan for JavaScript extension_points
        :test_dir: a directory to scan for JavaScript extension_points which
                   are being tested before they are added to the module
        """

        log.info('Creating MokshaExtensionPointMiddleware')
        self.application = application

        # if debug is False condense javascript to optimize
        self.__debug = config.get('moksha.extension_points.debug')
        self.__extension_cache = {}
        self.application = application

        if test_dir:
            self.load_extension_dir(test_dir)

        for ep in pkg_resources.iter_entry_points(entry_point):
            mod = ep.load()
            dir = os.path.dirname(mod.__file__)
            self.load_extension_dir(dir)

    def chunk_code(self, js, filename):
        start = js.find('{')
        end = 0
        chunks = []
        length = len(js)

        while (start != -1):
            count = 1
            i = start + 1
            pull_info = False
            pull_info_start = 0
            pull_info_end = 0

            while(count != 0 and i < length):
                if js[i] == '{':
                    count += 1
                elif js[i] == '}':
                    count -= 1
                elif count==1 and js[i]=='i' and js.find('info',i) == i:
                    if pull_info_start != 0:
                        print "ERROR: Unexpected Info Field : extension file %s has more than on info field per extension (ignoring file)" % filename
                        return None

                    # put us on info duty
                    pull_info = True

                if pull_info:
                    if pull_info_start == 0:
                        if count > 1:
                            pull_info_start = i
                    else:
                        if count == 1:
                            pull_info_end = i
                            pull_info = False

                i += 1

            end = i

            c = Chunk()
            c.code = js[start:end]
            c.info = js[pull_info_start:pull_info_end + 1]

            c.parse_consumes_field()
            chunks.append(c)

            if i >= length:
                print "ERROR: Unexpected EOF: extension file %s has mismatched braces (ignoring file)" % filename
                return None

            start = js.find('{', end)

        return chunks

    def load_extension(self, file):
        log.info("Loading JavaScript extension %s" % file)
        f = open(file,'r')
        js = f.read()

        chunks = self.chunk_code(js, file)
        if not chunks:
            if chunks != None:
                log.warning("No Content : extension file %s doesn't have any valid extensions (ignoring file)" % filename)

            return

        for c in chunks:
            for exttype in c.consumes:
                code = self.__extension_cache.get(exttype, [])
                #TODO: run through optimizer which strips whitespace
                code.append(c.code)
                self.__extension_cache[exttype] = code

    def load_extension_dir(self, dir):
        for root, dirs, files in os.walk(dir):
            for name in files:
                if name.endswith('js'):
                    path = os.path.join(root, name)
                    self.load_extension(path)

        # compile lists in the cache down to a string so we don't have to
        # process it on each request
        for key, value in self.__extension_cache.iteritems():
            s = '[' + ','.join(value) + ']'
            self.__extension_cache[key] = s

    def strip_script(self, environ, path):
        # Strips the script portion of a url path so the middleware works even
        # when mounted under a path other than root
        if path.startswith('/') and 'SCRIPT_NAME' in environ:
            prefix = environ.get('SCRIPT_NAME')
            if prefix.endswith('/'):
                prefix = prefix[:-1]

            if path.startswith(prefix):
                path = path[len(prefix):]

        return path

    def __call__(self, environ, start_response):

        request = Request(environ)

        path = self.strip_script(environ, request.path)
        if path.startswith('/moksha_extension_point'):
            exttype = request.params.get('exttype')
            if not exttype:
                response = Response('')
            else:
                extensions_data = self.__extension_cache.get(exttype, "")
                extensions_str = ','.join(extensions_data)

                script = 'var moksha_loaded_extensions ='
                script += extensions_data
                script += ';'
                # now run the deferred extensions queued up while the scripts
                # were being downloaded

                script += 'moksha.extensions._extension_cache["' + exttype +'"] = moksha_loaded_extensions;'
                script += 'var deferred=moksha.extensions._extension_deferred["' + exttype +'"];'
                script += 'var d=deferred.shift();'
                script += 'while(d){'
                script +=   'moksha.extensions.run_extensions(moksha_loaded_extensions, d);'
                script +=   'd = deferred.shift();'
                script += '}'

                response = Response(script)
        else:
            response = request.get_response(self.application)

        return response(environ, start_response)

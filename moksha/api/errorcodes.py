from paste.response import replace_header

class ErrObj(dict):
    def __init__(self, code, msg):
        super(ErrObj, self).__init__(code=code, msg=msg)

    def __getattribute__(self, name):
        try:
            return super(ErrObj, self).__getattribute__(name)
        except AttributeError, e:
            if name in self:
                return self[name]

            raise e

    def replace_app_header(self, app, header_name):
        if app.headers:
            headers = list(app.headers)
        else:
            headers = []

        replace_header(headers, header_name, self.code)
        app.headers = headers

    def __repr__(self):
        # act as if the user requested the code
        return str(self['code'])

class ErrEnum(object):
    def __init__(self, prefix, *errs):
        self._prefix = prefix
        self._code_map = {}

        for number, e in enumerate(errs):
            # we prefix the code so we can validate
            code = '%s_%d' % (prefix, number)
            eob = ErrObj(code, e[1])
            setattr(self, e[0], eob)
            setattr(self, code, eob)
            self._code_map[code] = e[0]

    def is_valid_class(self, err_code):
        if err_code.beginswith(self._prefix + '_'):
            return True

        return False

    def code_to_attr(self, code):
        return self._code_map[code]

    def attr_to_code(self, attr):
        return self.__getattribute__(attr).code

    def attr_to_message(self, attr):
        return self.__getattribute__(attr).msg

    def get_code(self, attr):
        return self.attr_to_code(attr)

    def get_message(self, attr):
        return self.attr_to_message(attr)

    def __call__(self, err_code):
        return self.get_message(err_code)

login_err = ErrEnum ('login_err',
                     ('USERNAME_PASSWORD_ERROR',
                  ('The username or password you entered is not valid. Please '
                   'try again.')
                 ),
                 ('UNKOWN_AUTH_ERROR',
                  ('An unknown error occurred while trying to log you in. '
                   'Please try again later or notify an admin if the problem '
                   'persists')
                 )
                )
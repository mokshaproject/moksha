from paste.response import replace_header
from moksha.lib.helpers import CategoryEnum

class ErrEnum(CategoryEnum):
    def attr_to_message(self, attr):
        return self.attr_to_data(attr)

    def get_message(self, attr):
        return self.get_data(attr)

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
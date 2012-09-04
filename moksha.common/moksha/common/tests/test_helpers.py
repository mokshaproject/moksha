import mock

# This is moved in python3.
# TODO -- use six.StringIO
import StringIO

from nose.tools import eq_

import moksha.common.lib.helpers

@mock.patch("sys.stdout", new_callable=StringIO.StringIO)
def test_trace(mock_stdout):

    @moksha.common.lib.helpers.trace
    def my_function(a, b):
        return None

    my_function(2, b=4)

    value = mock_stdout.getvalue()
    eq_(value, "my_function((2, 4), {}) = None\n")

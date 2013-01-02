import os
import moksha.common.config
from nose.tools import eq_


def test_config():
    expected = 'test_value 123'
    os.environ['test_variable'] = expected
    p = moksha.common.config.EnvironmentConfigParser()
    filename = '/'.join(__file__.split('/')[:-1] + ['/test_config.ini'])
    p.read(filenames=[filename])
    actual = p.get('test', 'test')
    eq_(actual, expected)

# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""

from tg.testutil import DBTest
from nose.tools import eq_

from mokshaplugin import model


class TestModel(DBTest):
    """The base class for testing models in you TG project."""
    model = model


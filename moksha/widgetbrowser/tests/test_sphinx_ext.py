import os
import shutil
from unittest import TestCase
from pkg_resources import resource_filename
import sphinx

doc_dir = resource_filename('widgetbrowser.tests', 'testdocs')

class TestSphinxExt(TestCase):
    def setUp(self):
        self.dest_dir = os.tempnam()
        if not os.path.isdir(self.dest_dir):
            os.makedirs(self.dest_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.dest_dir)
        except OSError:
            pass

    def test_generate(self):
        out = sphinx.main(['sphinx-build', doc_dir, self.dest_dir])
        self.failUnless(not out, out)
        html = open(os.path.join(self.dest_dir, 'index.html')).read()
        self.failUnless('widgetbrowser' in html)
        self.failUnless('x-large' in html)

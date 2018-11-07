import sys
import unittest
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log = logging.getLogger(__file__)


class TestUtils(unittest.TestCase):

    def test_templates(self):
        from .. import template_utils
        t = template_utils.apply_kv_to_files('tmpl', 'a template changed me', './files/', '.xml')
        self.assertTrue(len(t) == 1)


if __name__ == "__main__":
    t = TestUtils()
    t.test_del_type()

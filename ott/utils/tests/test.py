from .. import file_utils

import os
import sys
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log = logging.getLogger(__file__)

FILES_DIR = os.path.join(file_utils.get_file_dir(__file__), 'files')

class TestUtils(unittest.TestCase):

    def test_templates(self):
        from .. import template_utils
        t = template_utils.apply_kv_to_files('tmpl', 'a template changed me', FILES_DIR, '.xml', rewrite=False)
        self.assertTrue(len(t) == 1)

    def test_config_get_item(self):
        """ test get single item from config"""
        from ..config_util import ConfigUtil
        c = ConfigUtil(section="section_uno", run_dir=FILES_DIR)
        v = c.get('string')
        self.assertTrue(v == 'hi')

    def test_config_get_int(self):
        """ test get entire section (as dict) from config """
        from ..config_util import ConfigUtil
        c = ConfigUtil(section="section_dos", run_dir=FILES_DIR)
        v = c.get_int('section')
        self.assertTrue(v == 2)

    def test_config_get_seciton(self):
        """ test get entire section (as dict) from config """
        from ..config_util import ConfigUtil
        c = ConfigUtil(section="section_dos", run_dir=FILES_DIR)
        v = c.get_section()
        self.assertTrue(v.get('string') == "low")

if __name__ == "__main__":
    t = TestUtils()
    t.test_del_type()

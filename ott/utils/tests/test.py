from .. import file_utils
from .. import template_utils
from ..config_util import ConfigUtil

import os
import sys
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log = logging.getLogger(__file__)

FILES_DIR = os.path.join(file_utils.get_file_dir(__file__), 'files')

class TestUtils(unittest.TestCase):

    def test_config_get_item(self):
        """ test get single item from config"""
        c = ConfigUtil(section="section_uno", run_dir=FILES_DIR)
        v = c.get('string')
        self.assertTrue(v == 'hi')

    def test_config_get_int(self):
        """ test get entire section (as dict) from config """
        c = ConfigUtil(section="section_dos", run_dir=FILES_DIR)
        v = c.get_int('section')
        self.assertTrue(v == 2)

    def test_config_get_seciton(self):
        """ test get entire section (as dict) from config """
        c = ConfigUtil(section="section_dos", run_dir=FILES_DIR)
        v = c.get_section()
        self.assertTrue(v.get('string') == "low")


    def test_template_kv(self):
        to = 'a template changed me'
        t = template_utils.apply_kv_to_files('tmpl', to, FILES_DIR, '.xml', rewrite=False)
        self.assertTrue(len(t) == 1)
        self.assertTrue(to in t[0].get('applied'))

    def test_template_dict(self):
        # step 1: get kv dict from config
        to = "TEmPL_TEmPL_TEmPL"
        c = ConfigUtil(section="template_section", run_dir=FILES_DIR)
        kv = c.get_section()
        self.assertTrue(kv.get('tmpl') == to)

        # step 2: the test
        t = template_utils.apply_kvdict_to_files(kv, FILES_DIR, '.xml', rewrite=False)
        self.assertTrue(len(t) == 1)
        self.assertTrue(to in t[0].get('applied'))


if __name__ == "__main__":
    t = TestUtils()
    t.test_del_type()

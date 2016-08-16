import os
import sys
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log = logging.getLogger(__file__)

from ott.utils import web_utils


SOLR_URL = "http://maps7.trimet.org:10880/solr/core/update"
THIS_DIR = os.path.dirname(__file__)

class TestSolr(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_data(self):
        ''' test adding a document to a SOLR index
            @TODO: query SOLR and test whether the
        '''
        #import pdb; pdb.set_trace()
        status = web_utils.post_file(SOLR_URL, os.path.join(THIS_DIR, "add.xml"))
        self.assertTrue(status == 200)
        status = web_utils.post_data(SOLR_URL, "<commit/>")
        self.assertTrue(status == 200)

    def test_delete_data(self):
        '''
        '''
        #import pdb; pdb.set_trace()
        status = web_utils.post_file(SOLR_URL, os.path.join(THIS_DIR, "del.xml"))
        self.assertTrue(status == 200)
        status = web_utils.post_data(SOLR_URL, "<commit/>")
        self.assertTrue(status == 200)


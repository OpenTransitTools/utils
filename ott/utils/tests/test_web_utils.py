import os
import sys
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log = logging.getLogger(__file__)

from ott.utils import web_utils


SOLR_URL = "http://maps7.trimet.org:10880/solr/core/update"
THIS_DIR = os.path.dirname(__file__)

class TestWebUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_http_post(self):
        ''' test adding a document to a SOLR index with web_utils.post_file and post_data routines
            @TODO: query SOLR and test whether the data is both added and deleted
        '''
        #import pdb; pdb.set_trace()

        # add and comment data
        status = web_utils.post_file(SOLR_URL, os.path.join(THIS_DIR, "add.xml"))
        self.assertTrue(status == 200)
        status = web_utils.post_data(SOLR_URL, "<commit/>")
        self.assertTrue(status == 200)

        # delete this data
        status = web_utils.post_file(SOLR_URL, os.path.join(THIS_DIR, "del.xml"))
        self.assertTrue(status == 200)
        status = web_utils.post_data(SOLR_URL, "<commit/>")
        self.assertTrue(status == 200)


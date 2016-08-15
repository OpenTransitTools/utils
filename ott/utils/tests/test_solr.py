import os
import inspect
import unittest
import logging
log = logging.getLogger(__file__)


from ott.utils import web_utils

SOLR_URL = "http://maps7.trimet.org:10880/solr/core/update"

class TestSolr(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_del_type(self):
        '''
        '''
        web_utils.post(SOLR_URL, "<delete><query>type_name:BIKETOWN</query></delete>")
        web_utils.post(SOLR_URL, "<commit/>")

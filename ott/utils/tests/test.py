import sys
import unittest
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)


SOLR_URL = "http://maps7.trimet.org:10880/solr/core/update"

class TestSolr(unittest.TestCase):
#class TestSolr(object):

    def test_del_type(self):
        '''
        '''
        log.error("blah")
        log.warn("blah")
        log.info("blah")
        print "XXX"
        assert(False != True)

if __name__ == "__main__":
    t = TestSolr()
    t.test_del_type()

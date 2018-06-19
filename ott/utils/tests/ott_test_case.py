import os
import sys
import unittest
import urllib
import contextlib

from ott.utils import config_util
from ott.utils import file_utils


class OttTestCase(unittest.TestCase):
    domain = "localhost"
    port = "33333"
    path = None
    url_file = None
    ini = None

    def get_url(self, svc_name, params=None, lang=None):
        if self.path:
            ret_val = "http://{}:{}/{}/{}".format(self.domain, self.port, self.path, svc_name)
        else:
            ret_val = "http://{}:{}/{}".format(self.domain, self.port, svc_name)
        if params:
            ret_val = "{0}?{1}".format(ret_val, params)
        if lang:
            ret_val = "{0}&_LOCALE_={1}".format(ret_val, lang)
        if self.url_file:
            url = ret_val.replace(" ", "+")
            self.url_file.write(url)
            self.url_file.write("\n")
        return ret_val

    def call_url(self, url):
        ret_json = None
        print(u"{} test -- URL: {}".format(self.__class__.__name__, url))
        with contextlib.closing(urllib.urlopen(url)) as f:
            ret_json = f.read()
        return ret_json

    def setUp(self):
        #import pdb; pdb.set_trace()
        dir = file_utils.get_project_root_dir()
        ini = config_util.ConfigUtil('development.ini', run_dir=dir)
        self.ini = ini

        port = ini.get('ott.test_port', 'app:main')
        if not port:
            port = ini.get('ott.svr_port', 'app:main', self.port)
        self.port = port

        url_file = ini.get('ott.test_urlfile', 'app:main')
        if url_file:
            self.url_file = open(os.path.join(dir, url_file), "a+")

        test_domain = ini.get('ott.test_domain', 'app:main')
        if test_domain:
            self.domain = test_domain

        test_path = ini.get('ott.test_path', 'app:main')
        if test_path:
            self.path = test_path

    def tearDown(self):
        if self.url_file:
            self.url_file.flush()
            self.url_file.close()

    def call_url_match_list(self, url, list):
        u = self.call_url(url)
        for l in list:
            self.assertRegexpMatches(u, l)

    def call_url_match_string(self, url, str):
        u = self.call_url(url)
        self.assertRegexpMatches(u, str)

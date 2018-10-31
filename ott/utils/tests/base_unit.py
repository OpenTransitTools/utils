import unittest

from ott.utils import json_utils
from ott.utils import file_utils


class BaseUnit(unittest.TestCase):
    def setUp(self):
        self.base_path = file_utils.get_module_dir(self.__class__)

    def tearDown(self):
        pass

    def csv(self, file_name, validate_element=None):
        file_path = file_utils.path_join(self.base_path, file_name)
        csv = file_utils.make_csv_reader(file_path, validate_element)
        return csv

    def json(self, file_name):
        file_path = file_utils.path_join(self.base_path, file_name)
        json = json_utils.file_to_json(file_path)
        return json

    def call(self, url):
        ret_val = False
        return ret_val

    def call_test(self, url, has_attribute=None, in_attribute=None):
        """"""
        ret_val = False
        try:
            r = self.call(url)
            if r:
                if has_attribute:
                    if in_attribute:
                        pass
                    else:
                        ret_val = True
                else:
                    ret_val = True
        except:
            pass
        return ret_val
import unittest

from ott.utils import json_utils
from ott.utils import file_utils
import requests


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

    def call_test(self, url, find_attribute=None, in_attribute=None):
        """"""
        ret_val = False
        r = requests.get(url).json()
        if r:
            if find_attribute:
                a = r.get(find_attribute)
                if a:
                    if in_attribute:
                        if in_attribute in find_attribute:
                            ret_val = True
                    elif len(a) > 0:
                        ret_val = True
            elif r is not None:
                ret_val = True
        return ret_val
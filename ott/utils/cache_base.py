import os
import inspect

from ott.utils import file_utils
from ott.utils.config_util import ConfigUtil


class CacheBase(object):
    cache_expire = 31
    def_section = 'cache'

    def __init__(self, section='cache'):
        self.def_section = section
        self.cache_expire = self.config.get_int('cache_expire', 'cache', self.cache_expire)

    @property
    def config(self):
        config = ConfigUtil.factory(section=self.def_section)
        return config

    @property
    def this_module_dir(self):
        ''' set object property 'this_module_dir' to the file directory where the 'self' object lives
        '''
        file = inspect.getsourcefile(self.__class__)
        dir = os.path.dirname(os.path.abspath(file))
        return dir

    @property
    def cache_dir(self):
        ''' returns dir path ... makes the directory if it doesn't exist
        '''
        cache_dir = os.path.join(self.this_module_dir, "cache")
        file_utils.mkdir(cache_dir)
        return cache_dir

    @property
    def tmp_dir(self):
        tmp_dir = os.path.join(self.this_module_dir, "tmp")
        file_utils.mkdir(tmp_dir)
        return tmp_dir

    def is_fresh_in_cache(self, file):
        ''' determine if file exists and is newer than the cache expire time
        '''
        ret_val = False
        try:
            # NOTE if the file isn't in the cache, we'll get an exception
            age = file_utils.file_age(file)
            if age < self.cache_expire:
                ret_val = True
        except:
            ret_val = False
        return ret_val

    def cp_cached_file(self, file_name, destination_dir):
        ''' copy file from our cache to some other directory
        '''
        file = os.path.join(self.cache_dir, file_name)
        dest = os.path.join(destination_dir, file_name)
        file_utils.cp(file, dest)

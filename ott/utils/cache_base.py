import os
import inspect
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import web_utils
from ott.utils.config_util import ConfigUtil


class CacheBase(object):
    cache_dir_name = "cache"
    cache_expire = 31
    _config = None

    def __init__(self, section="cache", cache_dir_name="cache"):
        self._config = ConfigUtil.factory(section=section)
        self.cache_expire = self.config.get_int('cache_expire', 'cache', self.cache_expire)
        self.cache_dir_name = cache_dir_name

    @property
    def config(self):
        #import pdb; pdb.set_trace()
        if self._config is None:
            self._config = ConfigUtil.factory(section='cache')
        return self._config

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
        cache_dir = os.path.join(self.this_module_dir, self.cache_dir_name)
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

    def simple_cache_item_update(self, file_name, url, force_update=False):
        ''' check a cache file to see whether it needs updating...if so,
            then replace cached file with new version via wget on a  url
        '''
        file_path = os.path.join(self.cache_dir, file_name)

        # step 1: check the cache whether we should update or not
        update = force_update
        if not force_update and not self.is_fresh_in_cache(file_path):
            update = True

        # step 2: backup then wget new feed
        if update:
            log.info("wget {} to cache {}".format(url, file_path))
            file_utils.bkup(file_path)
            web_utils.wget(url, file_path)

        return update

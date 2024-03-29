from . import file_utils
from . import web_utils
from .config_util import ConfigUtil

import os
import inspect
import logging
log = logging.getLogger(__file__)


class CacheBase(object):
    cache_expire = 31
    _cache_dir = None
    _config = None

    def __init__(self, section="cache", cache_dir=None):
        # import pdb; pdb.set_trace()
        # step 0: config junk
        self._config = ConfigUtil.factory(section=section)
        self.cache_expire = self.config.get_int('cache_expire', 'cache', self.cache_expire)

        # step 1 - 3: create some type of cache dir
        # step 1: if cache dir not passed in or configured someplace ???
        if cache_dir is None and self.config.get('cache_dir'):
            d = self.config.ini_dir_path
            f = self.config.get('cache_dir')
            cache_dir = file_utils.path_join(d, f)

        # step 2: try to create any specified / configured cache directory
        if cache_dir:
            file_utils.mkdir(cache_dir)

        # step 3: haven't yet gotten a cache dir, so lets try to find and/or create a default
        #         cache dir local to this module directory
        if file_utils.exists(cache_dir) is False:
            cache_dir_name = self.config.get(section='cache', id='dir_name', def_val="cache")
            cache_dir = os.path.join(self.this_module_dir, cache_dir_name)
            file_utils.mkdir(cache_dir)

        # step 4: assign internal cache dir variable
        assert cache_dir is not None
        self._cache_dir = cache_dir

    @property
    def config(self):
        if self._config is None:
            self._config = ConfigUtil.factory(section='cache')
        return self._config

    @property
    def this_module_dir(self):
        """
        set object property 'this_module_dir' to the file directory where the 'self' object lives
        """
        file = inspect.getsourcefile(self.__class__)
        dir = os.path.dirname(os.path.abspath(file))
        return dir

    @property
    def cache_dir(self):
        """ returns dir path ... see constructor above
        """
        return self._cache_dir

    @property
    def tmp_dir(self):
        tmp_dir = os.path.join(self.this_module_dir, "tmp")
        file_utils.mkdir(tmp_dir)
        return tmp_dir

    def sub_dir(self, dir_name):
        """
        make path to random named dir
        """
        ret_val = os.path.join(self.this_module_dir, dir_name)
        return ret_val

    @classmethod
    def is_recent(cls, file, recent_days=1):
        """
        determine if file exists and is newer (in days) than the recent_days param (default 1 day)
        """
        ret_val = False
        try:
            # note: if the file isn't in the cache, we'll get an exception (thus not recent)
            age = file_utils.file_age(file)
            if age <= recent_days:
                ret_val = True
        except:
            ret_val = False
        return ret_val

    def is_fresh_in_cache(self, file):
        """ determine if file exists and is newer that cache_expire (default 31 days) """
        return self.is_recent(file, self.cache_expire)

    def cp_cached_file(self, file_name, destination_dir):
        """
        copy file from our cache to some other directory
        """
        file = os.path.join(self.cache_dir, file_name)
        dest = os.path.join(destination_dir, file_name)
        file_utils.cp(file, dest)

    def simple_cache_item_update(self, file_name, url, force_update=False):
        """
        check a cache file to see whether it needs updating...if so,
        then replace cached file with new version via wget on a  url
        """
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

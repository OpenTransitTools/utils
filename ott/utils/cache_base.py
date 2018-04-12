import os
import inspect
import logging
log = logging.getLogger(__file__)

from ott.utils import file_utils
from ott.utils import web_utils
from ott.utils.config_util import ConfigUtil


class CacheBase(object):
    cache_dir = None
    cache_expire = 31
    _config = None

    def __init__(self, section="cache", cache_dir=None):
        self._config = ConfigUtil.factory(section=section)
        self._make_cache_dir(cache_dir)
        self.cache_expire = self.config.get_int('cache_expire', 'cache', self.cache_expire)

    def _make_cache_dir(self, cache_dir, def_name="cache"):
        # step 1: if cache dir not passed in or configured someplace ???
        if cache_dir is None and self.config.get('cache_dir'):
            d = self.config.dir_path()
            f = self.config.get('cache_dir')
            cache_dir = file_utils.path_join(d, f)

        # step 2: try to create any specified / configured cache directory
        if cache_dir:
            file_utils.mkdir(cache_dir)
            self.cache_dir = cache_dir

        # step 3: haven't yet gotten a cache dir, so lets try to find and/or create a default cache dir local
        #         to this module directory
        if file_utils.exists(self.cache_dir) is False:
            self.cache_dir = os.path.join(self.this_module_dir, def_name)
            file_utils.mkdir(cache_dir)

    @property
    def config(self):
        # import pdb; pdb.set_trace()
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
        return self.cache_dir

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

    def is_fresh_in_cache(self, file):
        """
        determine if file exists and is newer (in days) than the numer of days to of cache expire
        """
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

from ConfigParser import SafeConfigParser
import sys
import logging
import logging.config
log = logging.getLogger(__file__)

from ott.utils import json_utils
from ott.utils import object_utils

SECTION='view'
INI=['app.ini', 'client.ini', 'services.ini', 'view.ini', 'production.ini']


class ConfigUtil(object):
    section = SECTION
    ini = INI
    found_ini = None

    def __init__(self, ini=None, section=None):
        if ini:     self.ini = ini
        if section: self.section = section

    @property
    def parser(self):
        ''' make the config parser
        '''
        candidates = []
        for i in self.ini:
            # add the .ini file and ./config/.ini file to our candidate file list
            candidates.append(i)
            candidates.append('./config/' + i)

        scp = SafeConfigParser()
        self.found_ini = scp.read(candidates)
        return scp

    def get(self, id, section=None, def_val=None):
        ''' get config value
        '''
        ret_val = def_val
        try:
            if section is None: section = self.section
            ret_val = self.parser.get(section, id)
            if ret_val is None:
               ret_val = def_val
        except Exception, e:
            log.info("Couldn't find '{0}' in config under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_int(self, id, section=None, def_val=None):
        ''' get config value as int (or go with def_val)
        '''
        ret_val = self.get(id, section, def_val)
        try:
            if ret_val:
                ret_val = int(ret_val)
        except Exception, e:
            log.info("Couldn't convert '{0}' value into an INT type under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_json(self, id, section=None):
        str_val = self.get(id, section=section)
        ret_val = json_utils.str_to_json(str_val, str_val)
        return ret_val

    @classmethod
    def config_logger(cls, ini):
        try:
            logging.config.fileConfig(ini, disable_existing_loggers=False)
        except Exception, e:
            pass

    @classmethod
    def factory(clfs, section=None, argv=sys.argv):
        #import pdb; pdb.set_trace()
        ini = INI
        if argv and '-ini' in argv:
            i = argv.index('-ini')
            ini = object_utils.str_to_list(argv[i + 1])
        cfg = ConfigUtil(ini, section)
        return cfg




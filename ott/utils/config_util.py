from ConfigParser import SafeConfigParser
import os
import sys
import logging
import logging.config
log = logging.getLogger(__file__)

from ott.utils import json_utils
from ott.utils import object_utils

SECTION='view'
INI=['app.ini', 'client.ini', 'services.ini', 'view.ini', 'production.ini']
run_dir=None

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

        # capture the execution directory in a global, as we're likely to cd out of here at some point
        global run_dir
        if run_dir is None:
            run_dir = os.getcwd()

        candidates = []
        for i in self.ini:
            # add the .ini file and ./config/.ini file to our candidate file list
            cfg = os.path.join("config", i)
            candidates.append(os.path.abspath(i))
            candidates.append(os.path.abspath(cfg))
            candidates.append(os.path.abspath(os.path.join(run_dir, i)))
            candidates.append(os.path.abspath(os.path.join(run_dir, cfg)))

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

    def get_float(self, id, section=None, def_val=None):
        ''' get config value as float (or go with def_val)
        '''
        ret_val = self.get(id, section, def_val)
        try:
            if ret_val:
                ret_val = float(ret_val)
        except Exception, e:
            log.info("Couldn't convert '{0}' value into a FLOAT type under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_bbox(self, section=None):
        ''' get config value as float (or go with def_val)
        '''
        top = self.get('top', section, 0.0)
        bottom = self.get('bottom', section, 0.0)
        left = self.get('left', section, 0.0)
        right = self.get('right', section, 0.0)
        try:
            top = float(top)
            bottom = float(bottom)
            left = float(left)
            right = float(right)
        except Exception, e:
            log.info("Couldn't convert top/bottom/left/right values to FLOATs under section '{0}'\n{1}".format(section, e))
        return top,bottom,left,right

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
        ''' create a Config object ... uses argv to override default list of .ini files
        '''
        #import pdb; pdb.set_trace()
        ini = INI
        if argv and '-ini' in argv:
            i = argv.index('-ini')
            ini = object_utils.str_to_list(argv[i + 1])
        cfg = ConfigUtil(ini, section)
        return cfg




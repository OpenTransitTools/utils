from ott.utils import file_utils
from ott.utils import object_utils

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import sys
import logging
log = logging.getLogger(__file__)

SECTION = 'view'
INI = ['app.ini', 'client.ini', 'services.ini', 'view.ini', 'production.ini', 'staging.ini', 'development.ini']


# global vars
CONFIG_SINGLETON = None  # only 1 instance of ConfigUtil is necessary ... save overhead by creating once
RUN_DIR = None


def set_run_dir(dir=None):
    global RUN_DIR
    RUN_DIR = dir


class ConfigUtil(object):
    section = SECTION
    log_ini = 'log.ini'
    ini = INI
    _parser = None

    found_ini = False
    ini_dir_path = None
    ini_file_path = None

    def __init__(self, ini=None, section=None, run_dir=None):
        if ini:
            if isinstance(ini, basestring):
                v = [ini]
                self.ini = v
            else:
                self.ini = ini
        if section:
            self.section = section
        if run_dir:
            set_run_dir(run_dir)

        # IMPORTANT: call make parser to dot Is and cross Ts ... fills out ini_dir_path & ini_file_path
        self._make_parser()

    @property
    def parser(self):
        """
        get the config (making it if necessary)
        NOTE: we use a SINGLETON, since only 1 parser is necessary and needed
        """
        global CONFIG_SINGLETON
        if CONFIG_SINGLETON is None:
            CONFIG_SINGLETON = self._make_parser()
        self._parser = CONFIG_SINGLETON
        return self._parser

    def _make_parser(self):
        """ make the config parser (SafeConfigParser) ... file lookup relative to the directory you run your app from
        """
        # import pdb; pdb.set_trace()
        # capture the execution directory in a global, as we're likely to cd out of here at some point
        global RUN_DIR
        if RUN_DIR is None:
            RUN_DIR = os.getcwd()

        self.logging_cfg()

        candidates = []
        for i in self.ini:
            # add the .ini file and ./config/.ini file to our candidate file list
            c = self.get_candidates(name=i)
            if c:
                candidates = candidates + c

        # create the config parser and read the .ini files
        scp = configparser.SafeConfigParser()
        paths = scp.read(candidates)

        # set variables
        if paths and len(paths):
            for p in paths:
                if file_utils.exists(p):
                    self.found_ini = True
                    self.ini_file_path = p
                    self.ini_dir_path = file_utils.get_file_dir(p)
                    break

        return scp

    def get(self, id, section=None, def_val=None):
        """ get config value
        """
        ret_val = def_val
        try:
            if section is None: section = self.section
            ret_val = self.parser.get(section, id)
            if ret_val is None:
               ret_val = def_val
        except Exception as e:
            log.info("Couldn't find '{0}' in config under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_section(self, section=None):
        """ get config value
        """
        ret_val = None
        try:
            if section is None: section = self.section
            ret_val =  dict(self.parser.items(section))
        except Exception as e:
            log.info("Couldn't find '{0}' in config under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_os_section(self, os, section):
        os_section = "{}_{}".format(os, section)
        return self.get_section(os_section)

    def find_os_section(self, section):
        import platform
        os = platform.system()
        return self.get_os_section(os, section)

    def get_int(self, id, section=None, def_val=None):
        """ get config value as int (or go with def_val)
        """
        ret_val = self.get(id, section, def_val)
        try:
            if ret_val:
                ret_val = int(ret_val)
        except Exception as e:
            log.info("Couldn't convert '{0}' value into an INT type under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_bool(self, id, section=None, def_val=False):
        """ get config value as boolean (string w/in .ini can be either True or true)
        """
        ret_val = self.get(id, section, def_val)
        return ret_val == True or ret_val == "True" or ret_val == "true"

    def get_float(self, id, section=None, def_val=None):
        """ get config value as float (or go with def_val)
        """
        ret_val = self.get(id, section, def_val)
        try:
            if ret_val:
                ret_val = float(ret_val)
        except Exception as e:
            log.info("Couldn't convert '{0}' value into a FLOAT type under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_list(self, id, section=None, def_val=None):
        """ get config value as list (comma separated)
        """
        ret_val = self.get(id, section, def_val)
        try:
            if ret_val:
                ret_val = [v.strip('[] \n\r\t') for v in ret_val.split(',')]
        except Exception as e:
            log.info("Couldn't convert '{0}' value into a LIST type under section '{1}'\n{2}".format(id, section, e))
        return ret_val

    def get_bbox(self, section=None):
        """ get config value as float (or go with def_val)
        """
        top    = self.get_float('top',    section)
        bottom = self.get_float('bottom', section)
        left   = self.get_float('left',   section)
        right  = self.get_float('right',  section)
        return top,bottom,left,right

    def get_json(self, id, section=None):
        from ott.utils import json_utils
        ret_val = None
        str_val = self.get(id, section=section)
        if str_val:
            ret_val = json_utils.str_to_json(str_val, str_val)
        return ret_val

    @classmethod
    def config_logger(cls, ini):
        try:
            logging.config.fileConfig(ini, disable_existing_loggers=False)
        except Exception as e:
            pass

    @classmethod
    def logging_cfg(cls):
        """ config the logging module
        """
        try:
            log_ini = cls.find_candidate("log.ini")
            if log_ini:
                logging.config.fileConfig(log_ini)
        except Exception as e:
            log.info(e)

    @classmethod
    def get_candidates(cls, name, config="config"):
        ret_val = []
        cfg = os.path.join(config, name)
        ret_val.append(os.path.abspath(name))
        ret_val.append(os.path.abspath(cfg))
        ret_val.append(os.path.abspath(os.path.join(RUN_DIR, name)))
        ret_val.append(os.path.abspath(os.path.join(RUN_DIR, cfg)))
        ret_val.append(os.path.join(os.path.expanduser("~"), name))
        ret_val.append(os.path.join(os.path.expanduser("~"), cfg))
        return ret_val

    @classmethod
    def find_candidate(cls, name, config="config", def_val=None):
        ret_val = def_val
        candidates = cls.get_candidates(name, config)
        for c in candidates:
            if os.path.exists(c):
                ret_val = c
                break
        return ret_val

    @classmethod
    def factory(cls, section=None, argv=sys.argv):
        """ create a Config object ... uses argv to override default list of .ini files
        """
        ini = INI
        if argv and '-ini' in argv:
            i = argv.index('-ini')
            ini = object_utils.str_to_list(argv[i + 1])
        cfg = ConfigUtil(ini, section)
        return cfg




from ConfigParser import SafeConfigParser
import json
import logging
import logging.config
log = logging.getLogger(__file__)


SECTION='view'
INI=['app.ini', 'client.ini', 'services.ini', 'view.ini', 'production.ini']


class OttConfig(object):
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
        ret_val = None
        str_val = None
        try:
            str_val = self.get(id, section=section)
            ret_val = json.loads(str_val)
        except Exception, e:
            log.info("Problems marshaling '{0}' into a python (json) object ({0} = {1}) \n{2}".format(id, str_val, e))
            ret_val = str_val
        return ret_val

    @classmethod
    def config_logger(cls, ini):
        try:
            logging.config.fileConfig(ini, disable_existing_loggers=False)
        except Exception, e:
            pass

    @classmethod
    def factory(clfs, argv=None, section=None):
        #import pdb; pdb.set_trace()
        ini = INI
        if argv and 'ini' in argv:
            ini = argv['ini']
        cfg = OttConfig(ini, section)
        return cfg




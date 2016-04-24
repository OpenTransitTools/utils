from ConfigParser import SafeConfigParser
import json
import logging
log = logging.getLogger(__file__)
import logging.config


SECTION='view'
INI=['app.ini', 'client.ini', 'services.ini', 'view.ini', 'production.ini']
parser = None
found_ini = None


def get_parser(ini=INI):
    ''' make the config parser
    '''
    global parser
    global found_ini

    try:
        if parser is None:
            candidates = []
            for i in ini:
                # add the .ini file and ./config/.ini file to our candidate file list
                candidates.append(i)
                candidates.append('./config/' + i)

            parser = SafeConfigParser()
            found_ini = parser.read(candidates)
    except Exception, e:
        log.info("Couldn't find an acceptable ini file from {0}\n{1}".format(candidates, e))

    return parser

def config_logger(ini=INI):
    try:
        get_parser(ini)
        logging.config.fileConfig(found_ini, disable_existing_loggers=False)
    except Exception, e:
        pass

def get(id, def_val=None, section=SECTION):
    ''' get config value
    '''
    ret_val = def_val
    try:
        if get_parser():
            ret_val = get_parser().get(section, id)
            if ret_val is None:
                ret_val = def_val
    except Exception, e:
        log.info("Couldn't find '{0}' in config under section '{1}'\n{2}".format(id, section, e))

    return ret_val

def get_int(id, def_val=None, section=SECTION):
    ''' get config value as int (or go with def_val)
    '''
    ret_val = def_val
    try:
        v = get(id, def_val, section)
        if v:
            ret_val = int(v)
    except Exception, e:
        log.info("Couldn't find int value '{0}' in config under section '{1}'\n{2}".format(id, section, e))

    return ret_val

def get_json(id, section=SECTION):
    ret_val = None
    str_val = None
    try:
        str_val = get(id, section=section)
        ret_val = json.loads(str_val)
    except Exception, e:
        log.info("Problems marshaling '{0}' into a python (json) object ({0} = {1}) \n{2}".format(id, str_val, e))
        ret_val = str_val
    return ret_val


class OttConfig(object):
    section = SECTION

    def __init__(section=SECTION):
        self.section = section

    def get(self, id, def_val=None, section=None): return get(id, def_val, section or self.section)
    def get_int(self, id, def_val=None, section=None): return get(id, def_val, section or self.section)
    def get_json(self, id, section=None): return get(id, section or self.section)



import logging.config

from ConfigParser import SafeConfigParser
import glob

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
    except:
        log.info("Couldn't find an acceptable ini file from {0}...".format(candidates))

    return parser


def config_logger(ini=INI):
    try:
        get_parser(ini)
        logging.config.fileConfig(found_ini, disable_existing_loggers=False)
    except Exception, e:
        pass


def get(id, def_val=None, section='view'):
    ''' get config value
    '''
    ret_val = def_val
    try:
        if get_parser():
            ret_val = get_parser().get(section, id)
            if ret_val is None:
                ret_val = def_val
    except:
        log.info("Couldn't find '{0}' in config under section '{1}'".format(id, section))

    return ret_val


def get_int(id, def_val=None, section='view'):
    ''' get config value as int (or go with def_val)
    '''
    ret_val = def_val
    try:
        v = get(id, def_val, section)
        if v:
            ret_val = int(v)
    except:
        log.info("Couldn't find int value '{0}' in config under section '{1}'".format(id, section))

    return ret_val

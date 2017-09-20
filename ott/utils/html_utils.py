import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils import date_utils
from ott.utils import num_utils


def get_domain_port(request):
    ret_val = request
    return ret_val

def planner_form_params(request):
    """ TODO ... move to  view are refactored/updated)
    """
    # step 0: default values for the trip planner form 
    dt = date_utils.get_day_info()
    tm = date_utils.get_time_info()

    walk_max_def = 1609
    bike_max_def = 4828
    def_max_dist = walk_max_def
    def_optimize = "QUICK"

    # TODO: make this work...
    # TODO: make 
    if 'Bike' in 'request':
        def_max_dist = bike_max_def
        def_optimize = "SAFE"


    ret_val = {
        "fromPlace" : None,
        "fromCoord" : None,
        "toPlace"   : None,
        "toCoord"   : None,
        "Hour"      : tm['hour'],
        "Minute"    : tm['minute'],
        "AmPm"      : "am" if tm['is_am'] else "pm",
        "is_am"     : tm['is_am'],
        "month"     : dt['month'],
        "day"       : dt['day'],
        "year"      : dt['year'],
        "numdays"   : dt['numdays'],
        "Arr"       : False,
        "Walk"      : def_max_dist,
        "optimize"  : def_optimize,
        "mode"      : "TRANSIT,WALK"
    }

    # step 1: get params dict
    params = params_to_dict(request)

    # step 2: blanket assignment
    for k,v in params.items():
        #import pdb; pdb.set_trace()
        if k in ret_val and v is not None and len(v) > 0:
            if type(ret_val[k]) == bool:
                ret_val[k] = (v == 'True')
            if type(ret_val[k]) == int:
                ret_val[k] = num_utils.to_int(v, ret_val[k]) 
            else:
                ret_val[k] = v

    # step 3: handle from & to
    if "from" in params and len(params["from"]) > 0:
        parts = params["from"].split("::") 
        ret_val["fromPlace"] = parts[0]
        if len(parts) > 1:
            ret_val["fromCoord"] = parts[1]

    if "to" in params and len(params["to"]) > 0:
        parts = params["to"].split("::") 
        ret_val["toPlace"] = parts[0]
        if len(parts) > 1:
            ret_val["toCoord"] = parts[1]

    # step 4: special handle other params...
    ret_val["is_am"] = True if ret_val['AmPm'] == "am" else False
    ret_val["min"] = ret_val["optimize"]  # TODO remove me by changing min to optimize all over...

    return ret_val


def params_to_dict(request):
    """ turn Pyramid's  MultDict of GET params to a normal dict.  
        multi-values will only use the first param value (and save off all to special _all param)
    """
    ret_val = {}
    try:
        params = request.params.mixed()
        # loop through the params and assign them to the return variable
        for key, value in params.items():
            # only use the first value of a list (but save off other values to a _all variable
            if isinstance(value, (list, tuple)):
                ret_val[key] = value[0]
                ret_val[key + "_all"] = value
            else:
                ret_val[key] = value

        # save off the full query string into this dict too...
        #TODO: this is a good idea, bad implementation == makes the URL grow expo-large REALLY BAD 
        #if request.query_string and len(request.query_string) > 0:
        #    ret_val['query_string'] = request.query_string 
    except:
        # assume that request is the dict / string for params, and hope for the best...
        ret_val = request

    return ret_val


def get_param_as_list(request, name, prim=str):
    """ utility function to parse a request object for a certain value (and return an integer based on the param if it's an int)
    """
    ret_val = []
    try:
        p = get_first_param(request, name)  # get param
        l = p.split(',')                    # split the list on commas
        ret_val = map(prim, l)              # cast the values to a certain built-in (or 'primitive' in java) type
    except:
        log.warn('uh oh...')

    return ret_val


def get_first_param_as_int(request, name, def_val=None):
    """ utility function to parse a request object for a certain value (and return an integer based on the param if it's an int)
    """
    ret_val=get_first_param(request, name, def_val)
    try:
        ret_val = int(ret_val)
    except:
        pass
    return ret_val


def get_first_param_as_float(request, name, def_val=None):
    """ utility function to parse a request object for a certain value (and return an integer based on the param if it's an int)
    """
    ret_val=get_first_param(request, name, def_val)
    try:
        ret_val = float(ret_val)
    except:
        pass
    return ret_val

def get_first_param_is_a_coord(request, name, def_val=False):
    """ looks for a string, which has a comma (assuming lat,lon) and is at least 7 chars in length ala 0.0,0.0
    """
    from ott.utils import geo_utils
    ret_val = def_val
    try:
        val = get_first_param(request, name, def_val)
        if geo_utils.is_coord(val):
            ret_val = True
    except:
        pass
    return ret_val


def get_first_param_as_coord(request, name, def_val=None, to_float=False):
    """ return lat,lon floats
    """
    from ott.utils import geo_utils
    val = get_first_param(request, name, def_val)
    lat,lon = geo_utils.ll_from_str(val, def_val, to_float)
    return lat,lon


def get_first_param_as_boolean(request, name, def_val=False):
    """ utility function to get a variable
    """
    ret_val = def_val

    val=get_first_param(request, name, def_val)
    try:
        if isinstance(val, bool):
            ret_val = val
        elif isinstance(val, str) or isinstance(val, unicode):
            if val.lower() == 'true':
                ret_val = True
            else: 
                ret_val = False
    except:
        pass
    return ret_val


def get_first_param_as_date(request, name='date', fmt='%m/%d/%Y', def_val=None):
    """ utility function to parse a request object for something that looks like a date object...
    """
    if def_val is None:
        def_val = datetime.date.today()

    ret_val = def_val
    try:
        dstr = get_first_param(request, name)
        if dstr is not None:
            ret_val = datetime.datetime.strptime(dstr, fmt).date()
    except:
        pass
    return ret_val


def get_first_param_as_str(request, name, def_val=None):
    return get_first_param(request, name, def_val)


def get_first_param_safe_str(request, name, max_len=60, strip_url=False, def_val=None):
    """ return a string, of which check the lenght and also strip out <> chars to prevent 
        xss vulnerabilities.  Further, there's a psudo-markdown markup language added to 
        replace certain strings with bold, italic, etc... chars.
        
        bold  = **bold***  = <b>bold</b> 
        italics  = _*italics*_  = <i>italics</i> 
        bold italics  = _**bold italics**_  = <b><i>bold italics</i></b> 
        strikeout = ~~strikeout~~~ = <s>strikeout</s>
        underline = __underline___ = <u>underline</u>
        url link = "mm[bbb](/link.html)" becomes "mm<a href='/link.html>bbb</a>" (only 1 link allowed)
    """
    ret_val = def_val
    s = get_first_param(request, name)
    if s:
        # first, trim down the url
        if max_len > 0 and len(s) <= max_len:
            s = s[0:max_len]

        # next, replace special chars with html markup
        ret_val = s.replace("<", "").replace(">", "").replace("&lt;", "").replace("&rt;", "") \
            .replace("_**", "<b><i>").replace("**_", "</i></b>") \
            .replace("_*", "<i>").replace("*_", "</i>")  \
            .replace("***", "</b>").replace("**", "<b>") \
            .replace("___", "</u>").replace("__", "<u>") \
            .replace("~~~", "</s>").replace("~~", "<s>")

        #
        # markup link parse
        # will turn "mm[bbb](/link.html)" into "mm<a href='/link.html>bbb</a>"
        #
        #import pdb; pdb.set_trace()
        br = ret_val.find("](")
        if br > 0:
            cs = ret_val.find("[")
            ue = ret_val.find(")")
            if cs < br < ue:
                pre = ret_val[:cs]
                ctn = ret_val[cs+1:br]
                url = ret_val[br+2:ue]
                post = ret_val[ue+1:]
                if strip_url:
                    ret_val = "{}{}{}".format(pre, ctn, post)
                else:
                    ret_val = "{}<a href='{}' target='#'>{}</a>{}".format(pre, url, ctn, post)

        return ret_val


def get_first_param(request, name, def_val=None):
    """
        utility function

        @return the first value of the named http param (remember, http can have multiple values for the same param name), 
        or def_val if that param was not sent via HTTP
    """
    ret_val=def_val
    try:
        l = request.params.getall(name)
        if l and len(l) > 0:
            ret_val = l[0]
    except:
        pass
    return ret_val


def get_ini_param(request, name, def_val=None):
    """ pyramid request has a simple way to get a named .ini parameter
    """
    ret_val = def_val
    try:
        ret_val = request.registry.settings[name]
    except Exception, e:
        pass
    return ret_val


def get_lang(request, def_val="en"):
    return get_first_param(request, "_LOCALE_", def_val)


def unescape_html_str(html_str, def_val=""):
    ret_val = def_val
    try:
        # python 3.3+
        import html
        ret_val = html.unescape(html_str)
    except:
        # python 2.7
        import HTMLParser
        ret_val = HTMLParser.HTMLParser().unescape(html_str)
    return ret_val


def unescape_html(dict_list):
    """ replace html escaped &lt; and &gt; characters with < or >
        @see: http://stackoverflow.com/questions/1076536/replacing-values-in-a-python-list-dictionary
    """
    for datadict in dict_list:
        for key, value in datadict.items():
            m = value.replace("&lt;", "<").replace("&gt;", ">")
            datadict[key] = m


html_escape_table = {
        " ": "%20",
        "&": "%26",
        '"': "%22",
        "'": "%27",
        ">": "%3E",
        "<": "%3C",
}


def html_escape(text):
    """ escape chars -- http://wiki.python.org/moin/EscapingHtml
    """
    ret_val = text
    try:
        ret_val = "".join(html_escape_table.get(c, c) for c in text)
    except:
        pass
    return ret_val


def html_escape_num(num):
    """ escape numbers ... and make sure we handle 'Infinity' numbers (else, json will not be well-formed).
    """
    ret_val = num
    try:
        if isinstance(num, basestring) or num == float("Inf"):
            num = str(num)
            pass
        ret_val = num
    except:
        pass
    return ret_val



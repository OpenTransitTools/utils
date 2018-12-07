import time
import datetime
from datetime import timedelta
from calendar import monthrange

from . import num_utils
from . import object_utils

import logging
log = logging.getLogger(__file__)


def ret_me(s):
    return s


_ = ret_me

MORE = _('more')
TODAY = _('Today')


def get_local_time():
    return time.localtime()


def get_local_date():
    return datetime.date.today()


def get_hour(tm=None):
    """ return hour from input time as int
    """
    if tm is None:
        tm = get_local_time()
    return tm.tm_hour


def get_day_before(year=None, month=None, day=None, num_days=1):
    """ return a datetime.date for the day before specified date
        NOTE: if no params sent, default is yesterday
    """
    dt = get_local_date()
    y = num_utils.to_int(year, dt.year)
    m = num_utils.to_int(month, dt.month)
    d = num_utils.to_int(day, dt.day)
    day = datetime.date(y, m, d)
    before = day - datetime.timedelta(days=num_days)
    return before


def is_today(month, day, def_val=False):
    """ return True if month and day are same as today, else return False
        if either day or month are None, return def_val
    """
    ret_val = def_val
    if month and day:
        dt = get_local_date()
        if day == dt.day and month == dt.month:
            ret_val = True
        else:
            ret_val = False
    return ret_val


def get_time_info(tm=None):
    """ gets a dict with a few params based on input date-time object
    """
    if tm is None:
        tm = get_local_time()
    ret_val = {
        'hour'    : int(time.strftime('%I', tm).lstrip('0')),
        'minute'  : int(time.strftime('%M', tm)), 
        'is_am'   : time.strftime('%p', tm) == 'AM'
    }
    return ret_val


def get_day_info(dt=None):
    """ gets a dict with a few params based on input date-time object
    """
    if dt is None:
        dt = get_local_date()

    st,end=monthrange(dt.year, dt.month)
    ret_val = {
        'year'    : dt.year,
        'month'   : dt.month,
        'm_abbrv' : dt.strftime("%b"),
        'm_name'  : dt.strftime("%B"),
        'numdays' : end,
        'day'     : dt.day
    }
    return ret_val


def parse_month_day_year_string(mdy_str, sep='/'):
    """ convert MM/DD/YYYY string into parts
    """
    p = mdy_str.split(sep)
    ret_val = {
        'month' : object_utils.list_val(p, 0),
        'day'   : object_utils.list_val(p, 1),
        'year'  : object_utils.list_val(p, 2)
    }
    return ret_val


def normalize_year(input_month, input_year=None):
    """ This routine is used when we only have month parameters (text planner / stop schedule lookup) and the
        year is implied...

        RULES:
          return last year if we're w/in a few months of the new year, today is in the months of Jan-March and the search month is Sept-Dec
          return next year if we're w/in a few months of the new year, today is in the months of April-Dec and the search month is this month - 3 
          return this year otherwise...
    """
    today = get_local_date()

    input_year  = num_utils.to_int(input_year,  today.year)
    input_month = num_utils.to_int(input_month, today.month)

    ret_val = input_year
    if today.month < 4:       # This is JAN, FEB or MARCH
        if input_month > 8:   # and we want to see a month SEPT, OCT, NOV, DEC
            ret_val = input_year - 1
    else:                                    # This is APRIL - DEC
        if today.month > (input_month  + 3):  # and we want to see something > 3 months back....
            ret_val = input_year + 1
    return ret_val


def set_date(dt=None, month=None, day=None, year=None):
    """ return a datetime object, setting new month & day ranges
    """
    if dt is None:
        dt = get_local_date()

    ret_val = dt
    try:
        if not year : year  = dt.year
        if not month: month = dt.month
        if not day  : day   = dt.day
        ret_val = dt.replace(year, month, day)
    except:
        pass
    return ret_val


def pretty_time(dt=None, fmt=None, def_val=None):
    ret_val = def_val
    try:
        if fmt is None:
            fmt = ' %I:%M%p'
        if dt is None:
            dt = time
        ret_val = dt.strftime(fmt)
        ret_val = ret_val.lower().replace(' 0', '').strip()  # "3:40pm"
    except Exception as e:
        log.debug(e)
    return ret_val


def pretty_date(dt=None, fmt=None):
    if fmt is None:
        fmt = '%A, %B %d, %Y'
    if dt is None:
        dt = get_local_date()
    ret_val = dt.strftime(fmt).replace(' 0',' ')  # "Monday, March 4, 2013"
    return ret_val


def pretty_date_time(dt=None, date_fmt=None, time_format=None, sep_str=" @ "):
    d = pretty_date(dt, date_fmt)
    t = pretty_time(dt, time_format)
    ret_val = d
    if t and len(t) > 2:
        ret_val = "{}{}{}".format(d, sep_str, t)
    return ret_val


def pretty_date_from_ms(ms, fmt=None):
    dt = None
    try:
        if ms is not None:
            if isinstance(ms, (str, unicode)):
                ms = int(ms)
            dt = datetime.datetime.fromtimestamp(ms/1000.0)
    except Exception as e:
        log.info(e)
    ret_val = pretty_date(dt, fmt)
    return ret_val


def dow(dt=None, fmt='%A'):
    return pretty_date(dt, fmt)


def dow_abbrv(dt=None, fmt='%a'):
    return dow(dt, fmt)


def secs_since_epoch(t=None):
    if not t:
        t = get_local_date()
    secs = time.mktime(t.timetuple())
    return secs 


def test_for_date(date, def_val=None):
    """ make sure this is a date object """
    ret_val = date
    try:
        x = date.day
        x = date.month
        x = date.year
        ret_val = date
    except:
        try:
            # opps, was a datetime object ... return the date portion
            x = date.date.day
            x = date.date.month
            x = date.date.year
            ret_val = date.date
        except:
            if def_val == "NOW":
                ret_val = get_local_date()
            else:
                ret_val = def_val
    return ret_val


def is_distant(dt, days=35):
    """ test whether date time is in 'distant' past compared to today
    """
    ret_val = False
    today = get_local_date()
    if type(dt) is datetime.datetime:
        dt = dt.date()
    if type(dt) is datetime.date and today > dt and today - dt > timedelta(days=days):
        ret_val = True
    return ret_val


def is_past(secs, min_val=1000000000):
    """ test whether second is in the past compared to now in epoch seconds
    """
    ret_val = False
    now = secs_since_epoch()
    if secs > min_val and secs < now:
        ret_val = True
    return ret_val


def is_future(secs, min_val=1000000000):
    """ test whether second is in the future compared to now in epoch seconds 
    """
    ret_val = False
    now = secs_since_epoch()
    if secs > min_val and secs > now:
        ret_val = True
    return ret_val


def make_tab_obj(name, uri=None, date=None, append=None):
    """ for the date tab on the stop schedule page, we expect an object that has a name and a url
        this method builds that structure, and most importantly, the url for those tabs
    """
    ret_val = {}

    # put the name of the tab first (and strip off any leading / trailing ZEROs if the name is a date)
    ret_val["name"] = name.lstrip('0').replace('/0','/')

    # next give the tab object a URL ... date is broken up into month and day parts 
    if uri:
        month = ""
        day = ""
        if date:
            month = "&month={0}".format(date.month)
            day = "&day={0}".format(date.day)
        ret_val["url"] = "{0}{1}{2}".format(uri, month, day)
        if append:
            ret_val["url"] = "{0}&{1}".format(ret_val["url"], append)

    return ret_val


def get_svc_date_tabs(dt, uri, more_tab=True, translate=ret_me, fmt='%m/%d/%Y', smfmt='%m/%d', pttyfmt='%A, %B %d, %Y'):
    """ return 3 date strings representing the next WEEKDAY, SAT, SUN 
    """
    ret_val = []

    #import pdb; pdb.set_trace()

    # step 1: is 'today' the active tab, or is target date in future, so that's active, and we have a 'today' tab to left
    if get_local_date() == dt:
        ret_val.append(make_tab_obj(translate(TODAY)))
    else:
        ret_val.append(make_tab_obj(translate(TODAY), uri, get_local_date()))
        ret_val.append(make_tab_obj(dt.strftime(smfmt)))

    # step 2: figure out how many days from target is next sat, sunday and/or monday (next two service days different from today)
    delta1 = 1
    delta2 = 2
    if dt.weekday() < 5:
        # date is a m-f, so we're looking for next sat (delta1) and sun (delta 2)
        delta1 = 5 - dt.weekday()
        delta2 = delta1 + 1
    elif dt.weekday() == 6:
        # date is a sunday, so we're looking for monday (delta1), which is = 1 day off, and next sat (delta2) which is +6 days off 
        delta2 = 6

    d1 = dt + datetime.timedelta(days=delta1)
    d2 = dt + datetime.timedelta(days=delta2)
    #print "{0} {1} {2}={3} {4}={5}".format(dt, dt.weekday(), delta1, d1, delta2, d2)

    # step 3: add the next to service day tabs to our return array
    ret_val.append(make_tab_obj(d1.strftime(smfmt), uri, d1))
    ret_val.append(make_tab_obj(d2.strftime(smfmt), uri, d2))

    # TODO put the ret_val append stuff in a separate method that builds up the dict...
    #      and add a pretty_date to that dict, so that we can create a css TOOLTIP that shows what 
    #      weekday / date the 2/1, 2/5, 2/6 dates represent...
    #, "pretty_date": pretty_date(d1, pttyfmt)})

    # step 4: if we are not showing the date form, give the 'more' option which will show that form
    if more_tab:
        ret_val.append(make_tab_obj(translate(MORE), uri, dt, MORE))

    return ret_val


def str_to_date(str_date, fmt_list=['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y'], def_val=None):
    """ utility function to parse a request object for something that looks like a date object...
    """
    if def_val is None:
        def_val = get_local_date()

    ret_val = def_val
    for fmt in fmt_list:
        try:
            d = datetime.datetime.strptime(str_date, fmt).date()
            if d is not None:
                ret_val = d
                break
        except Exception as e:
            log.debug(e)
    return ret_val


def today_str(fmt='%m-%d-%Y'):
    date = get_local_date()
    ret_val = date.strftime(fmt)
    return ret_val


def date_to_str(date, fmt='%Y-%m-%d'):
    if date is None:
        date = get_local_date()

    ret_val = date
    if isinstance(date, datetime.date):
        ret_val = date.strftime(fmt)
    return ret_val


def make_date_from_timestamp(num, def_val=None):
    ret_val = def_val
    try:
        ret_val = datetime.datetime.fromtimestamp(num)
    except Exception as e:
        log.debug(e)
    return ret_val


def is_date_between(start, end, now=None):
    """ will compare a datetime (now) to a start and end datetime.
        the datetime being compared defaults to 'now()'
        if a date() submitted, then defaults will be added to turn that into a datetime() for date() at 12am
        if a time() is submitted, then defaults will be added to turn that into a datetime() of today at time()
    """
    ret_val = False

    try:
        if now is None:
            now = datetime.datetime.now()
        elif type(now) is datetime.date:
            now = datetime.datetime.combine(now, datetime.datetime.min.time())
        elif type(now) is datetime.time:
            now = datetime.datetime.combine(get_local_date(), now)

        if type(start) is datetime.datetime and type(end) is datetime.datetime:
            if start < now < end:
                ret_val = True
        elif type(start) is datetime.datetime:
            if start < now:
                ret_val = True
        elif type(end) is datetime.datetime:
            if now < end:
                ret_val = True
    except Exception as e:
        log.debug(e)
    return ret_val


def split_time(time):
    """ given 02:33:44 as a time string, return
    """
    h = None
    m = None
    try:
        t = time.split(":")
        h = int(t[0])
        m = int(t[1])
    except Exception as e:
        log.debug(e)
    return h, m


def now_time_code(time, now=None, tolerance_minutes=30):
    """ return a code comparing NOW to time string in milatary format
        return values:
            "E" = Earlier time than NOW
            "N" = NOW
            "L" = Later time than NOW
    """
    ret_val = "E"
    if now is None:
        now = datetime.datetime.now()

    tolerance_hours = 1
    if tolerance_minutes >= 60:
        tolerance_hours = (tolerance_minutes / 60) + 1
        tolerance_minutes = tolerance_minutes % 60

    try:
        h, m = split_time(time)
        if h > 23:
            h = h - 23

        if now.hour < h - tolerance_hours:
            ret_val - "E"
        elif now.hour > h - tolerance_hours:
            ret_val - "L"
        elif now.hour == h:
            if m < now.minute:
                ret_val = "E"
            elif m - now.minute <= tolerance_minutes:
                ret_val = "N"
            else:
                ret_val = "L"
        elif now.hour == h - tolerance_hours:
            r = 60 - now.minute
            if m < r:
                ret_val = "E"
            elif m - r <= tolerance_minutes:
                ret_val = "N"
            else:
                ret_val = "L"
    except:
        pass
    return ret_val


def military_to_english_time(time, fmt="{0}:{1:02d}{2}"):
    """ assumes 08:33:55 and 22:33:42 type times
        will return 8:33am and 10:33pm
        (not we floor the minutes)
    """
    ret_val = time
    try:
        h, m = split_time(time)
        ampm = "am"
        if h >= 12:
            ampm = "pm"
        if h >= 24:
            ampm = "am"
        h = h % 12
        if h == 0:
            h = 12

        ret_val = fmt.format(h, m, ampm)
    except:
        pass

    return ret_val

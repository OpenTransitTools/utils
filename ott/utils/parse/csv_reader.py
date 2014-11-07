import os
import csv
import datetime
import time
import urllib
from threading import Thread

import logging
log = logging.getLogger(__file__)


class Csv(object):
    csv_uri = None
    file = None
    reader = None
    raw_data = []
    last_update = None
    last_check = None
    delimiter=','

    def __init__(self, uri, delimiter=','):
        log.info('Reading CSV {0}'.format(uri))
        self.delimiter=delimiter
        self.assign_uri(uri)

    def assign_uri(self, uri):
        '''
        '''
        if '/' in uri or '\\' in uri:
            self.csv_uri = uri
        else:
            here = os.path.dirname(os.path.abspath(__file__))
            self.csv_uri = os.path.join(here, uri) 


    def open(self):
        '''
        '''
        log.debug("open rules {0}".format(self.csv_uri))
        if 'http' in self.csv_uri:
            '''
            TODO: this ....
            with contextlib.closing(urllib.urlopen(url)) as stream:
                otp = stream.read()
                ret_val = json.loads(otp)
            '''
            data = urllib.urlopen(self.csv_uri)

        else:
            data = open(self.csv_uri, 'rb')
            self.file = data
        #import pdb; pdb.set_trace()
        self.reader = csv.DictReader(data, delimiter=self.delimiter)


    def close(self):
        '''
        '''
        if self.file:
            self.file.close()
            self.file = None


    def read(self):
        ret_val = []
        self.open()
        for row in self.reader:
            ret_val.append(row)
        self.close()
        return ret_val


    def timed_refresh_check(self, n_minutes):
        ''' will check for new rules every N minutes (via the 'update_rules()' method), and
            trigger reloading of those rules if we've exceeded the n_minute time slice
            @todo: might we thread the rule refresh if we're pulling rules via the web???
        '''
        ret_val = False

        if n_minutes is None or n_minutes < 0:
            n_minutes = 15

        n_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=n_minutes)
        if self.last_check is None or self.last_check < n_minutes_ago:
            self.last_check = datetime.datetime.now()
            thread = Thread(target=self.new_data_check)
            thread.start()
            time.sleep(0.2)
            ret_val = True

        return ret_val


    def new_data_check(self):
        ''' open/download CSV of rules, and compare it existing rules 
            @return: True indicating that new data was reloaded...
        '''
        ret_val = False

        # step 1: grab new CSV data...
        new_data = self.read()
        self.last_check = datetime.datetime.now()
        log.debug('checking for new CSV data')

        # step 2: ...and compare whether the data changed from the last load of the rules 
        if new_data and len(new_data) > 0 and new_data != self.raw_data:

            # step 3: if the data did change, update the rules...
            self.update_data(new_data)
            ret_val = True

        return ret_val


    def update_data(self, new_data):
        ''' I'm probably overridden in sub classes
        '''
        self.raw_data = new_data
        self.last_update = datetime.datetime.now()


def main(argv):
    c = Csv(argv[1])
    c.open()
    fn = c.reader.fieldnames 
    #for i in fn: print i
    for row in c.reader:
        print row;

    c.close()


if __name__ == '__main__':
    import sys
    main(sys.argv)


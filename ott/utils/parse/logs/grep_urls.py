""" read a log file and summarize the number of requests within a time window
"""
from base import LogParseBase

HTTP = 'http://'
HTTPS = 'https://'

class GrepUrls(LogParseBase):
    """ parse an app.log file
        line should start with a time stamp "hh:mm:ss"
    """
    cache = {}
    filter = None

    def __init__(self, args):
        self.log_file = args.file_name
        self.filter = args.filter

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='request-count', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name', '-f', help='Log file', default="app.log")
        parser.add_argument('--filter', '-z', help='Optionally find urls based on search', default=None)
        args = parser.parse_args()
        return args

    def cache_url(self, line, key):
        #import pdb; pdb.set_trace()
        try:
            s = line.split(key)
            url = "{}{}".format(key, s[1].strip())
            cnt = 1
            if url in self.cache:
                cnt = self.cache[url] + 1
            self.cache[url] = cnt
        except Exception, e:
            print e

    def process(self):
        """ """
        with open(self.log_file) as f:
            for i, line in enumerate(f):
                if HTTP in line:
                    self.cache_url(line, HTTP)
                if HTTPS in line:
                    self.cache_url(line, HTTPS)

    def do_print(self):
        from collections import OrderedDict
        sorted_keys = sorted(self.cache, key=self.cache.get)
        for u in sorted_keys:
            print "url: {} == {} hit(s)".format(u, self.cache[u])


def main():
    rd = GrepUrls.factory()
    rd.process()
    rd.do_print()

if __name__ == "__main__":
    main()

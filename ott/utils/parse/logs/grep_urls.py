"""
read a log file and pull out random urls
examples:
    bin/log_grep_urls -f ../app.log -n 100 -j -u http://maps9.trimet.org/ride/planner.html -z plan_trip
    bin/log_grep_urls -f ../app.log -n 100 -j -u http://maps9.trimet.org/ride/header.html -z header
    bin/log_grep_urls -f ../app.log -n 100 -j -u http://maps9.trimet.org/ride/stop_schedule.html -z "stop_sch"
    bin/log_grep_urls -f ../app.log -n 100 -j -u http://maps9.trimet.org/ride/stop.html -z "stop?"
    bin/log_grep_urls -f ../app.log -n 100 -j -u http://maps9.trimet.org/ride/stops_near.html -z "stops_near"
    bin/log_grep_urls -f ../app.log -j -u http://maps9.trimet.org/ride/stops_near.html -z "stops_near"
    bin/log_grep_urls -f ../app.log
"""
import random
from base import Base

HTTP = 'http://'
HTTPS = 'https://'


class GrepUrls(Base):
    """ parse an app.log file
        line should start with a time stamp "hh:mm:ss"
    """
    cache = {}
    filter = None
    limit = 0
    just_args = False
    append_url = None

    def __init__(self, args):
        self.log_file = args.file_name
        self.filter = args.filter
        self.limit = args.num_results
        self.just_args = args.just_args
        self.append_url = args.append_url

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='grep-urls', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name', '-f', help='Log file', default="app.log")
        parser.add_argument('--filter', '-z', help='Optionally find urls based on search', default=None)
        parser.add_argument('--num_results', '-n', help='Return N random urls', default=0, type=int)
        parser.add_argument('--just_args', '-j', help='Return just the url args', action='store_true')
        parser.add_argument('--append_url', '-u', help='Append this url to the args', default=None)
        args = parser.parse_args()
        return args

    def cache_url(self, line, key):
        try:
            s = line.split(key)
            url = "{}{}".format(key, s[1].strip())
            cnt = 1
            if url in self.cache:
                cnt = self.cache[url] + 1
            self.cache[url] = cnt
        except Exception as e:
            print(e)

    def process(self):
        """ """
        with open(self.log_file) as f:
            for i, line in enumerate(f):
                if HTTP in line:
                    self.cache_url(line, HTTP)
                if HTTPS in line:
                    self.cache_url(line, HTTPS)

    def printer(self, url):
        count = self.cache[url]
        if self.just_args:
            u = ""
            if self.append_url:
                u = "{}?".format(self.append_url)
            args = url.split('?')[1]
            print("{}{}".format(u, args))
        else:
            print("url: {} == {} hit(s)".format(url, count))

    def do_print(self):
        #import pdb; pdb.set_trace()

        # step 1: if we want to limit the results, then we'll find a random skip number
        skips = tskips = hits = 0
        if self.limit:
            skips = tskips = random.randint(11, 111)


        from collections import OrderedDict
        sorted_keys = sorted(self.cache, key=self.cache.get)
        for i, k in enumerate(sorted_keys):

            # step 2: if we're looking for a certain url, let's filter other than those
            if self.filter and self.filter not in k:
                continue

            # step 3a: going to limit results
            if self.limit:
                # step 3b: so let's skip ahead a random amount
                if i < tskips:
                    continue
                tskips = tskips + skips * hits

                hits += 1
                if hits > self.limit:
                    break

            self.printer(k)


def main():
    GrepUrls.run()


if __name__ == "__main__":
    main()

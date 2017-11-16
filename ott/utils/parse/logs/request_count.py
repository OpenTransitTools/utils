""" read a log file and summarize the number of requests within a time window
"""
from base import LogParseBase


class LogInfo(object):
    line = []

    def __init__(self):
        pass

    def put(self, name, count):
        self.line.append({'name': name, 'count': count})

    def do_print(self, span, search_term=None, filter=None):
        t = ""
        if search_term:
            t = "(searching for term '{}')".format(search_term)
        print "\n\nnumber of requests {} for each {} minutes:\n".format(t, span)
        total = 0
        for l in self.line:
            if filter and not l['name'].startswith(filter):
                continue
            print "time: {} == {} requests".format(l['name'], l['count'])
            total += l['count']
        print "\ntotal requests: {}\n\n".format(total)


class RequestCount(LogParseBase):
    """ parse an app.log file
        line should start with a time stamp "hh:mm:ss"
    """
    info = LogInfo()
    increment = 0
    inc_name = "hourly"
    search = None
    filter = None

    def __init__(self, args):
        self.log_file = args.file_name
        self.search = args.search_term
        self.filter = args.filter
        if args.span:
            self.increment = 60 * 60
        else:
            self.increment = 10 * 60
            inc_name = "10 min"

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='request-count', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name', '-f', help='Log file', default="app.log")
        parser.add_argument('--search_term', '-s', help='Optional search term (line contains search_term)', default=None)
        parser.add_argument('--filter', '-z', help='Optional time filter (00 to 23) to only print that time window', default=None)
        parser.add_argument('--one_hour', '-o', dest='span', action='store_true')
        parser.add_argument('--ten_min', '-m', dest='span', action='store_false')
        parser.set_defaults(span=True)
        args = parser.parse_args()
        return args

    def process(self):
        """ """

        count = 0
        tens = 0
        hours = 0
        inc = self.increment
        with open(self.log_file) as f:
            for i, line in enumerate(f):
                if len(line) >= 8:
                    time_str = line[:8]
                    new_time = self.timestamp_to_seconds(time_str)
                else:
                    continue
                if new_time < inc:
                    if self.search and self.search not in line:
                        # import pdb; pdb.set_trace()
                        continue
                    count += 1
                else:
                    # info logger
                    ninc = inc + self.increment
                    if self.increment <= 600:
                        if tens > 5:
                            tens = 0
                            hours += 1
                        m1 = tens * 10
                        m2 = (tens + 1) * 10
                        tens += 1
                        name = "{:02d}:{:02d} to {:02d}:{:02d}".format(hours, m1, hours, m2)
                    else:
                        h1 = inc / self.increment - 1
                        h2 = ninc / self.increment - 1
                        name = "{:02d}:00 to {:02d}:00".format(h1, h2)

                    self.info.put(name, count)

                    inc = ninc
                    if self.search and self.search not in line:
                        count = 0
                    else:
                        count = 1

        # info logger - here to pick up last run of the loop (hate to cut-n-paste, but...)
        ninc = inc + self.increment
        if self.increment <= 600:
            if tens > 5:
                tens = 0
                hours += 1
            m1 = tens * 10
            m2 = (tens + 1) * 10
            tens += 1
            name = "{:02d}:{:02d} to {:02d}:{:02d}".format(hours, m1, hours, m2)
        else:
            h1 = inc / self.increment - 1
            h2 = ninc / self.increment - 1
            name = "{:02d}:00 to {:02d}:00".format(h1, h2)

        self.info.put(name, count)

    def do_print(self):
        self.info.do_print(self.inc_name, self.search, self.filter)


def main():
    rd = RequestCount.factory()
    rd.process()
    rd.do_print()

if __name__ == "__main__":
    main()

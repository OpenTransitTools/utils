""" read a log file and summarize the number of requests within a time window
"""
from base import LogParseBase


class LogInfo(object):
    line = []

    def __init__(self):
        pass

    def put(self, name, count):
        self.line.append({name: name, count: count})

    def do_print(self, span, search_term=None):
        t = ""
        if search_term:
            t = "(searching for term '{}')".format(search_term)
        print "\n\nnumber of requests {} for each {} minutes:\n".format(t, span)
        for l in self.line:
            print "  --> name: {} == {}\n".format(l.name, l.count)
        print "\n\n"


class RequestCount(LogParseBase):
    """ parse an app.log file
        line should start with a time stamp "hh:mm:ss"
    """
    info = LogInfo()
    span = 60

    def __init__(self, args):
        self.log_file = args.file_name
        self.min_distance = args.distance

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='request-count', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name', '-f',  help='Log file', default="app.log")
        parser.add_argument('--span', '-s',  help='Number of seconds to bracket', type=int, default=60)
        args = parser.parse_args()
        return args

    def process(self):
        #import pdb; pdb.set_trace()

        largest = 0
        old_time = 0

        with open(self.log_file) as f:
            last_line = None
            for i, line in enumerate(f):
                if len(line) >= 8:
                    time_str = line[:8]
                    new_time = self.timestamp_to_seconds(time_str)
                    if new_time is None:
                        continue
                    dist = new_time - old_time
                    if dist > self.min_distance:
                        self.number_of_delays += 1
                    if dist > largest:
                        #import pdb; pdb.set_trace()
                        largest = dist
                        self.info.set(last_line, line, i, dist)

                    old_time = new_time
                    last_line = line

            self.line_count = i


def main():
    rd = RequestDwell.factory()
    rd.process()
    rd.do_print()

if __name__ == "__main__":
    main()

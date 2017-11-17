""" read a log file and find the spot in the file with the longest pause between two subsequent timestamps
    example:
      bin/log_find_pauses -f ../app.log
"""
from base import Base


class LogInfo(object):
    pre_line = None
    lg_line = None
    lg_line_no = 0
    delay = 0

    def __init__(self):
        pass

    def set(self, pre_line, lg_line, lg_line_no, delay):
        self.pre_line = pre_line
        self.lg_line = lg_line
        self.lg_line_no = lg_line_no
        self.delay = delay

    def do_print(self, total_lines):
        print "\n longest delay: {} seconds ({} minutes) at line {} of {} \n\n line {}: {} \n line {}: {} \n".\
            format(self.delay, self.delay / 60, self.lg_line_no, total_lines, self.lg_line_no-1, self.pre_line, self.lg_line_no, self.lg_line)


class RequestDwell(Base):
    """ parse an app.log file
        line should start with a time stamp "hh:mm:ss"
    """
    info = LogInfo()
    line_count = 0
    number_of_delays = 0

    def __init__(self, args):
        self.log_file = args.file_name
        self.min_distance = args.distance

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='request-dwell', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name',  '-f',  help='Log file', default="app.log")
        parser.add_argument('--distance',   '-d',  help='Number of seconds to capture', type=int, default=60)
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

    def do_print(self):
        print "\n total number of delays that exceeded {} seconds:  {}".format(self.min_distance, self.number_of_delays)
        self.info.do_print(self.line_count)


def main():
    RequestDwell.run()


if __name__ == "__main__":
    main()

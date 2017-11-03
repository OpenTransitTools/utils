
#F="gap-log-halloween-11.50am"
F="gap-log-at-1.09pm"


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


class RequestDwell(object):
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
        parser = argparse.ArgumentParser(prog='log-dwell', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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

    @classmethod
    def timestamp_to_seconds(cls, time_str):
        """ take in a h:m:s string, ala 11:22:30 and return total seconds """
        ret_val = None
        try:
            h, m, s = time_str.split(':')
            ret_val = int(h) * 3600 + int(m) * 60 + int(s)
        except:
            pass
        return ret_val

    @classmethod
    def factory(cls):
        args = cls.get_args()
        inst = cls(args)
        return inst




def main():
    rd = RequestDwell.factory()
    rd.process()
    rd.do_print()

if __name__ == "__main__":
    main()

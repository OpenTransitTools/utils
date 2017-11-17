class Base(object):

    def process(self):
        pass

    def do_print(self):
        pass

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
    def get_args(cls):
        pass

    @classmethod
    def factory(cls):
        args = cls.get_args()
        inst = cls(args)
        return inst

    @classmethod
    def run(cls):
        inst = cls.factory()
        inst.process()
        inst.do_print()
        return inst

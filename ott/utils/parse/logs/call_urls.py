""" call urls from a log file

  examples:
    bin/log_grep_urls -f ../app.log
"""
from base import Base
from ott.utils import test_utils


class CallUrls(Base):
    """ call urls from file.urls
    """
    url_file = None
    results = None

    def __init__(self, args):
        self.url_file = args.file_name

    @classmethod
    def get_args(cls):
        import argparse
        parser = argparse.ArgumentParser(prog='call-urls', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--file_name', '-f', help='Urls file', default="app.urls")
        args = parser.parse_args()
        return args

    def process(self):
        """ """
        #import pdb; pdb.set_trace()
        self.results = test_utils.loop_urls(self.url_file)

    def do_print(self):
        print self.results


def main():
    CallUrls.run()


if __name__ == "__main__":
    main()

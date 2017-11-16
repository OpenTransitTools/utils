import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'simplejson',
    #'requests',
    #'twilio',
]

extras_require = dict(
    dev=[],
)

#
# eggs that you need if you're running a version of python lower than 2.7
#
if sys.version_info[:2] < (2, 7):
    requires.extend(['argparse>=1.2.1', 'unittest2>=0.5.1'])


setup(
    name='ott.utils',
    version='0.1.0',
    description='Open Transit Tools - OTT Utils',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    dependency_links=[],
    license="Mozilla-derived (http://opentransittools.com)",
    url='http://opentransittools.com',
    keywords='ott, otp, gtfs, gtfsdb, data, database, services, transit',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=requires,
    test_suite="ott.utils.tests",
    entry_points="""\
        [console_scripts]
        log_find_pauses = ott.utils.parse.logs.request_dwell:main
        log_count_requests = ott.utils.parse.logs.request_count:main
        log_grep_urls = ott.utils.parse.logs.grep_urls:main
    """,
)

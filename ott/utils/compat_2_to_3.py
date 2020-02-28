# py 3 removes basestring and long
try:
    basestring = basestring
except:
    basestring = str
try:
    long = long
except:
    long = int

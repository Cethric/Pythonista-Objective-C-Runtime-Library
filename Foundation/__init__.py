from ctypes import *

try:
    from dataTypes import *
except ImportError:
    from .dataTypes import *
    
try:
    from constants import *
except ImportError:
    from .constants import *

def NSMakeRange(location, length):
    r = NSRange(location, length)
    return r


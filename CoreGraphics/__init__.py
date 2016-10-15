# from ctypes import *

# try:
#     from .. import *
# except:
#     path = os.path.join(os.path.expanduser('~/Documents'), '')
#     if path not in sys.path:
#         sys.path.append(path)
#     from objc import *

try:
    from transforms import *
except (ImportError, SystemError):
    from .transforms import *
try:
    from geometry import *
except (ImportError, SystemError):
    from .geometry import *

CGClasses = [
    'CGBitmapContext',
    'CGColor',
    'CGColorSpace',
    'CGContext',
    'CGDataConsumer',
    'CGDataProvider',
    'CGFont',
    'CGFunction',
    'CGGradient',
    'CGImage',
    'CGLayer',
    'CGPath',
    'CGPattern',
    'CGPDFArray',
    'CGPDFContentStream',
    'CGPDFContext',
    'CGPDFContext',
    'CGPDFDictionary',
    'CGPDFDocument',
    'CGPDFObject',
    'CGPDFOperatorTable',
    'CGPDFPage',
    'CGPDFScanner',
    'CGPDFStream',
    'CGPDFString',
    'CGShading'
]


def loadCGClass(klass):
    if klass in CGClasses:
        return findClass(klass)
    raise ValueError("'{}' is not a CG Class".format(klass))


def main():
    import math

    print(CGAfflineTransformMake(0, 0, 0, 0, 1, 3))
    print(CGAffineTransformMakeRotation(math.radians(0)))
    print(CGAffineTransformMakeScale(10, 10))
    print(CGAffineTransformMakeTranslation(5, 10))
    print(CGAffineTransformTranslate(CGAffineTransformIdentity(), 10, 5))
    print(CGAffineTransformScale(CGAffineTransformIdentity(), 10, 5))
    print(CGAffineTransformRotate(
        CGAffineTransformIdentity(), math.radians(7)
    ))
    print(CGAffineTransformInvert(CGAffineTransformIdentity()))
    print(CGAffineTransformConcat(
        CGAffineTransformIdentity(),
        CGAffineTransformMakeRotation(math.radians(79))
    ))
    print(CGPointApplyAffineTransform(
        CGPoint(10, 10),
        CGAffineTransformIdentity()
    ))

if __name__ == '__main__':
    main()

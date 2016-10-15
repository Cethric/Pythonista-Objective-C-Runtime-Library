from ctypes import (
    Structure, CDLL, byref, POINTER, c_double, c_void_p, c_bool, c_int
)
c = CDLL(None)

CGFloat = c_double


class CGSize(Structure):
    _fields_ = [
        ('width', CGFloat),
        ('height', CGFloat),
    ]

    def __str__(self):
        return "<CGSize object at 0x{}" \
            "\n\t{},\t{}\n>".format(
                id(self),
                self.width, self.height,
            )


class CGPoint(Structure):
    _fields_ = [
        ('x', CGFloat),
        ('y', CGFloat),
    ]

    def __str__(self):
        return "<CGPoint object at 0x{}" \
            "\n\t{},\t{}\n>".format(
                id(self),
                self.x, self.y,
            )


class CGRect(Structure):
    _fields_ = [
        ('origin', CGPoint),
        ('size', CGSize),
    ]

    def __str__(self):
        return "<CGRect object at 0x{}" \
            "\n\t{},\t{}\n>".format(
                id(self),
                self.origin, self.size,
            )


class CGVector(Structure):
    _fields_ = [
        ('dx', CGFloat),
        ('dy', CGFloat)
    ]

    def __str__(self):
        return "<CGSize object at 0x{}" \
            "\n\t{},\t{}\n>".format(
                id(self),
                self.dx, self.dy,
            )

CGRectEdgeMinXEdge = 0
CGRectEdgeMinYEdge = 1
CGRectEdgeMaxXEdge = 2
CGRectEdgeMaxYEdge = 3


def CGPointCreateDictionaryRepresentation(point):
    func = c.CGPointCreateDictionaryRepresentation
    func.argtypes = [CGPoint]
    func.restype = c_void_p
    return func(point)


def CGSizeCreateDictionaryRepresentation(size):
    func = c.CGSizeCreateDictionaryRepresentation
    func.argtypes = [CGSize]
    func.restype = c_void_p
    return func(size)


def CGRectCreateDictionaryRepresentation(rect):
    func = c.CGRectCreateDictionaryRepresentation
    func.argtypes = [CGRect]
    func.restype = c_void_p
    return func(rect)


def CGPointMakeWithDictionaryRepresentation(cfdict, point):
    func = c.CGPointMakeWithDictionaryRepresentation
    func.argtypes = [c_void_p, POINTER(CGPoint)]
    func.restype = c_bool
    return func(cfdict, byref(point))


def CGSizeMakeWithDictionaryRepresentation(cfdict, size):
    func = c.CGSizeMakeWithDictionaryRepresentation
    func.argtypes = [c_void_p, POINTER(CGSize)]
    func.restype = c_bool
    return func(cfdict, byref(size))


def CGRectMakeWithDictionaryRepresentation(cfdict, rect):
    func = c.CGRectMakeWithDictionaryRepresentation
    func.argtypes = [c_void_p, POINTER(CGRect)]
    func.restype = c_bool
    return func(cfdict, byref(rect))


def CGPointMake(px, py):
    return CGPoint(px, py)


def CGRectMake(x, y, width, height):
    return CGRect(CGPoint(x, y), CGSize(width, height))


def CGSizeMake(width, height):
    return CGSize(width, height)


def CGVectorMake(dx, dy):
    return CGVector(dx, dy)


def CGRectDivide(rect, slice, remainder, amount, edge):
    func = c.CGRectDivide
    func.argtypes = [CGRect, POINTER(CGRect), POINTER(CGRect), CGFloat, c_int]
    func.restype = None
    return func(rect, byref(slice), byref(remainder), amount, edge)


def CGRectInset(rect, dx, dy):
    func = c.CGRectInset
    func.argtypes = [CGRect, CGFloat, CGFloat]
    func.restype = CGRect
    return func(rect, dx, dy)


def CGRectIntegral(rect):
    func = c.CGRectIntegral
    func.argtypes = [CGRect]
    func.restype = CGRect
    return func(rect)


def CGRectIntersection(r1, r2):
    func = c.CGRectIntersection
    func.argtypes = [CGRect, CGRect]
    func.restype = CGRect
    return func(r1, r2)


def CGRectOffset(rect, dx, dy):
    func = c.CGRectOffset
    func.argtypes = [CGRect, CGFloat, CGFloat]
    func.restype = CGRect
    return func(rect, dx, dy)


def CGRectStandardize(rect):
    func = c.CGRectStandardize
    func.argtypes = [CGRect]
    func.restype = CGRect
    return func(rect)


def CGRectUnion(r1, r2):
    func = c.CGRectUnion
    func.argtypes = [CGRect, CGRect]
    func.restype = CGRect
    return func(r1, r2)


def CGPointEqualToPoint(p1, p2):
    func = c.CGPointEqualToPoint
    func.argtypes = [CGPoint, CGPoint]
    func.restype = c_bool
    return func(p1, p2)


def CGSizeEqualToSize(p1, p2):
    func = c.CGSizeEqualToSize
    func.argtypes = [CGSize, CGSize]
    func.restype = c_bool
    return func(p1, p2)


def CGRectEqualToRect(p1, p2):
    func = c.CGRectEqualToRect
    func.argtypes = [CGRect, CGRect]
    func.restype = c_bool
    return func(p1, p2)


def CGRectIntersectsRect(p1, p2):
    func = c.CGRectIntersectsRect
    func.argtypes = [CGRect, CGRect]
    func.restype = c_bool
    return func(p1, p2)


def CGRectContainsPoint(p1, p2):
    func = c.CGRectContainsPoint
    func.argtypes = [CGRect, CGPoint]
    func.restype = c_bool
    return func(p1, p2)


def CGRectContainsRect(p1, p2):
    func = c.CGRectContainsRect
    func.argtypes = [CGRect, CGRect]
    func.restype = c_bool
    return func(p1, p2)


def CGRectGetMinX(rect):
    func = c.CGRectGetMinX
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetMinY(rect):
    func = c.CGRectGetMinY
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetMidX(rect):
    func = c.CGRectGetMidX
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetMidY(rect):
    func = c.CGRectGetMidY
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetMaxX(rect):
    func = c.CGRectGetMaxX
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetMaxY(rect):
    func = c.CGRectGetMaxY
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetWidth(rect):
    func = c.CGRectGetWidth
    func.argtypes = [CGRect]
    func.restype = CGFloat
    return func(rect)


def CGRectGetHeight(rect):
    func = c.CGRectGetHeight
    func.argtypes = [CGRect]
    func.restype = CGFloat


def CGRectIsEmpty(rect):
    func = c.CGRectIsEmpty
    func.argtypes = [CGRect]
    func.restype = c_bool
    return func(rect)


def CGRectIsNull(rect):
    func = c.CGRectIsNull
    func.argtypes = [CGRect]
    func.restype = c_bool
    return func(rect)


def CGRectIsInfinite(rect):
    func = c.CGRectIsInfinite
    func.argtypes = [CGRect]
    func.restype = c_bool
    return func(rect)


__all__ = [
    'CGFloat', 'CGRect', 'CGSize', 'CGPoint', 'CGVector', 'CGRectEdgeMinXEdge',
    'CGRectEdgeMinYEdge', 'CGRectEdgeMaxXEdge', 'CGRectEdgeMaxYEdge',
    'CGPointCreateDictionaryRepresentation',
    'CGSizeCreateDictionaryRepresentation',
    'CGRectCreateDictionaryRepresentation',
    'CGPointMakeWithDictionaryRepresentation',
    'CGSizeMakeWithDictionaryRepresentation', 'CGPointMake', 'CGRectMake',
    'CGSizeMake', 'CGVectorMake', 'CGRectDivide', 'CGRectInset',
    'CGRectIntegral', 'CGRectIntersection', 'CGRectOffset',
    'CGRectStandardize', 'CGRectUnion', 'CGPointEqualToPoint',
    'CGSizeEqualToSize', 'CGRectEqualToRect', 'CGRectIntersectsRect',
    'CGRectContainsPoint', 'CGRectContainsRect', 'CGRectGetMinX',
    'CGRectGetMinY', 'CGRectGetMidX', 'CGRectGetMidY', 'CGRectGetMaxX',
    'CGRectGetMaxY', 'CGRectGetWidth', 'CGRectGetHeight', 'CGRectIsEmpty',
    'CGRectIsNull', 'CGRectIsInfinite'
]

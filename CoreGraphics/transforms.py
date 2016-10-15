from ctypes import (
    CDLL, Structure, c_bool
)
c = CDLL(None)
try:
    from .geometry import (
        CGFloat, CGPoint, CGSize, CGRect
    )
except (ImportError, SystemError):
    from geometry import (
        CGFloat, CGPoint, CGSize, CGRect
    )


class CGAfflineTransform(Structure):
    _fields_ = [
        ('a', CGFloat),
        ('b', CGFloat),
        ('c', CGFloat),
        ('d', CGFloat),
        ('tx', CGFloat),
        ('ty', CGFloat),
    ]

    def __str__(self):
        return "<CGAfflineTransform object at 0x{}" \
            "\n\t{},\t{},\t0.0" \
            "\n\t{},\t{},\t0.0" \
            "\n\t{},\t{},\t1.0\n>".format(
                id(self),
                self.a, self.b,
                self.c, self.d,
                self.tx, self.ty
            )


def CGAffineTransformIdentity():
    return CGAfflineTransform(
        1, 0,  # 0
        0, 1,  # 0
        0, 0,  # 1
    )


def CGAfflineTransformMake(a, b, c, d, tx, ty):
    return CGAfflineTransform(a, b, c, d, tx, ty)


def CGAffineTransformMakeRotation(angle):
    func = c.CGAffineTransformMakeRotation
    func.argtypes = [CGFloat]
    func.restype = CGAfflineTransform
    r = func(angle)
    return CGAfflineTransformMake(r.a, r.b, r.c, r.d, 0, 0)


def CGAffineTransformMakeScale(sx, sy):
    func = c.CGAffineTransformMakeScale
    func.argtypes = [CGFloat, CGFloat]
    func.restype = CGAfflineTransform
    return func(sx, sy)


def CGAffineTransformMakeTranslation(tx, ty):
    func = c.CGAffineTransformMakeTranslation
    func.argtypes = [CGFloat, CGFloat]
    func.restype = CGAfflineTransform
    return func(tx, ty)


def CGAffineTransformTranslate(t, tx, ty):
    func = c.CGAffineTransformTranslate
    func.argtypes = [CGAfflineTransform, CGFloat, CGFloat]
    func.restype = CGAfflineTransform
    return func(t, tx, ty)


def CGAffineTransformScale(t, sx, sy):
    func = c.CGAffineTransformScale
    func.argtypes = [CGAfflineTransform, CGFloat, CGFloat]
    func.restype = CGAfflineTransform
    return func(t, sx, sy)


def CGAffineTransformRotate(t, angle):
    func = c.CGAffineTransformRotate
    func.argtypes = [CGAfflineTransform, CGFloat]
    func.restype = CGAfflineTransform
    return func(t, angle)


def CGAffineTransformInvert(t):
    func = c.CGAffineTransformInvert
    func.argtypes = [CGAfflineTransform]
    func.restype = CGAfflineTransform
    return func(t)


def CGAffineTransformConcat(t1, t2):
    func = c.CGAffineTransformConcat
    func.argtypes = [CGAfflineTransform, CGAfflineTransform]
    func.restype = CGAfflineTransform
    return func(t1, t2)


def CGPointApplyAffineTransform(point, t):
    func = c.CGPointApplyAffineTransform
    func.argtypes = [CGPoint, CGAfflineTransform]
    func.restype = CGPoint
    return func(point, t)


def CGSizeApplyAffineTransform(size, t):
    func = c.CGSizeApplyAffineTransform
    func.argtypes = [CGSize, CGAfflineTransform]
    func.restype = CGSize
    return func(size, t)


def CGRectApplyAffineTransform(rect, t):
    func = c.CGRectApplyAffineTransform
    func.argtypes = [CGRect, CGAfflineTransform]
    func.restype = CGRect
    return func(rect, t)


def CGAffineTransformIsIdentity(t):
    func = c.CGAffineTransformIsIdentity
    func.argtypes = [CGAfflineTransform]
    func.restype = c_bool
    return func(t)


def CGAffineTransformEqualToTransform(t1, t2):
    func = c.CGAffineTransformIsIdentity
    func.argtypes = [CGAfflineTransform, CGAfflineTransform]
    func.restype = c_bool
    return func(t1, t2)

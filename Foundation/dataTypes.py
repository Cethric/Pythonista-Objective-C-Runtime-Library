from ctypes import (
    c_long, c_ulong, c_int, c_double, c_void_p, c_uint, c_ushort, c_ulonglong,
    POINTER, Structure
)

NSInteger = c_long
NSUInteger = c_ulong
NSSocketNativeHandle = c_int
NSStringEncoding = NSUInteger
NSTimeInterval = c_double
NSZone = c_void_p


class NSDecimal(Structure):
    _fields_ = [
        ('_exponent', c_int),
        ('_length', c_uint),
        ('_isNegative', c_uint),
        ('_isCompact', c_uint),
        ('_reserved', c_uint),
        ('_mantissa', c_ushort * 8)
    ]


class NSRange(Structure):
    _fields_ = [
        ('_location', NSUInteger),
        ('length', NSUInteger),
    ]

    def __str__(self):
        return "<NSRange object at 0x{} LOC: {} LEN: {}>".format(
            id(self), self._location, self.length
        )

NSRangePointer = POINTER(NSRange)


class NSSwappedDouble(Structure):
    _fields_ = [
        ('v', c_ulonglong),
    ]


class NSSwappedFloat(Structure):
    _fields_ = [
        ('v', c_uint),
    ]



__all__ = [
    'NSInteger', 'NSUInteger', 'NSSocketNativeHandle', 'NSStringEncoding',
    'NSTimeInterval', 'NSZone', 'NSDecimal', 'NSRange', 'NSRangePointer',
    'NSSwappedDouble', 'NSSwappedFloat'
]

import functools
import ctypes

try:
    import CoreGraphics
except ImportError:
    from . import CoreGraphics

try:
    import Foundation
except ImportError:
    from . import Foundation

# "Official" constant names from objc/runtime.h.
_C_ID = '@'  # Object pointer, optionally followed by a quoted class name
# (if no class name is present, represents id)
_C_CLASS = '#'  # Class
_C_SEL = ':'  # Selector
_C_CHR = 'c'  # signed char (though the specification says just char)
_C_UCHR = 'C'  # unsigned char
_C_SHT = 's'  # short
_C_USHT = 'S'  # unsigned short
_C_INT = 'i'  # int
_C_UINT = 'I'  # unsigned int
_C_LNG = 'l'  # long
_C_ULNG = 'L'  # unsigned long
_C_LNG_LNG = 'q'  # long long
_C_ULNG_LNG = 'Q'  # unsigned long long
_C_FLT = 'f'  # float
_C_DBL = 'd'  # double or long double
_C_BFLD = 'b'  # Bit field, followed by the width in bits
_C_BOOL = 'B'  # _Bool or bool
_C_VOID = 'v'  # void
_C_UNDEF = '?'  # Unknown type, such as function pointers
_C_PTR = '^'  # Pointer, followed by the encoding for the pointed to type
_C_CHARPTR = '*'  # char *
# _C_ATOM = '%' # Atom? Not listed in the Objective-C Runtime Programming Guide
# Array brackets, containing the number of array elements,
# followed by the encoding for the element type
_C_ARY_B = '['
_C_ARY_E = ']'
# Union parentheses, containing the unqoted union name (? if unknown),
# optionally followed by an = and any number of encodings for the field type,
# each optionally preceded by a quoted field name
_C_UNION_B = '('
_C_UNION_E = ')'
# Struct braces, containing the unqoted struct name (? if unknown),
# optionally followed by an = and any number of encodings for the field type,
# each optionally preceded by a quoted field name
_C_STRUCT_B = '{'
_C_STRUCT_E = '}'
# _C_VECTOR = '!'  # Vector? Not listed in the
# Objective-C Runtime Programming Guide
_C_CONST = 'r'  # const qualifier

# "Unofficial" constant names for encodings listed in the Objective-C Runtime
# Programming Guide, but not in objc/runtime.h.

_C_IN = "n"  # in qualifier
_C_INOUT = "N"  # inout qualifier
_C_OUT = "o"  # out qualifier
_C_BYCOPY = "O"  # bycopy qualifier
_C_BYREF = "R"  # byref qualifier
_C_ONEWAY = "V"  # oneway qualifier

_SCALAR_ENCODING_MAP = {
    _C_CHR: "signed char",
    _C_UCHR: "unsigned char",
    _C_SHT: "short",
    _C_USHT: "unsigned short",
    _C_INT: "int",
    _C_UINT: "unsigned int",
    _C_LNG: "long",
    _C_ULNG: "unsigned long",
    _C_LNG_LNG: "long long",
    _C_ULNG_LNG: "unsigned long long",
    _C_FLT: "float",
    _C_DBL: "double",
    _C_BOOL: "bool",
}

_SCALAR_ENCODING_RMAP = {v: k for k, v in _SCALAR_ENCODING_MAP.items()}
_SCALAR_ENCODING_RMAP["char"] = _C_CHR


class BaseType(object):
    __slots__ = ()

    def encode(self):
        raise NotImplementedError()


class InternalType(BaseType):
    __slots__ = ()


class UnknownType(BaseType):
    __slots__ = ()

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}()".format(
            cls=type(self), self=self
        )

    def encode(self):
        return _C_UNDEF

UNKNOWN_TYPE = UnknownType()


class Void(BaseType):
    __slots__ = ()

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}()".format(
            cls=type(self), self=self
        )

    def encode(self):
        return _C_VOID

VOID = Void()


class Scalar(BaseType):
    __slots__ = ("type",)

    def __init__(self, type):
        super().__init__()
        self.type = type

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}({self.type!r})".format(
            cls=type(self), self=self
        )

    def encode(self):
        return _SCALAR_ENCODING_RMAP[self.type]

CHAR = Scalar("char")
SIGNED_CHAR = Scalar("signed char")
UNSIGNED_CHAR = Scalar("unsigned char")
SHORT = Scalar("short")
UNSIGNED_SHORT = Scalar("unsigned short")
INT = Scalar("int")
UNSIGNED_INT = Scalar("unsigned int")
LONG = Scalar("long")
UNSIGNED_LONG = Scalar("unsigned long")
LONG_LONG = Scalar("long long")
UNSIGNED_LONG_LONG = Scalar("unsigned long long")
FLOAT = Scalar("float")
DOUBLE = Scalar("double")
BOOL = Scalar("bool")


class BitField(InternalType):
    __slots__ = ("width",)

    def __init__(self, width):
        super().__init__()
        self.width = width

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}({self.width!r})".format(
            cls=type(self), self=self
        )

    def encode(self):
        return "{}{}".format(_C_BFLD, self.width)


class Pointer(BaseType):
    __slots__ = ("element_type",)

    def __init__(self, element_type):
        super().__init__()
        self.element_type = element_type

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.element_type!r})".format(cls=type(self), self=self)

    def encode(self):
        if isinstance(self.element_type, Scalar) and \
                self.element_type.type == "char":
            return _C_CHARPTR
        else:
            return "{}{}".format(_C_PTR, self.element_type.encode())


class ID(BaseType):
    __slots__ = ("class_name",)

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.class_name!r})".format(cls=type(self), self=self)

    def encode(self):
        if self.class_name is None:
            return _C_ID
        else:
            return '{}"{}"'.format(_C_ID, self.class_name)


class Class(BaseType):
    __slots__ = ()

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}()".format(
            cls=type(self), self=self
        )

    def encode(self):
        return _C_CLASS

CLASS = Class()


class Selector(BaseType):
    __slots__ = ()

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}()".format(
            cls=type(self), self=self
        )

    def encode(self):
        return _C_SEL

SELECTOR = Selector()


class Array(BaseType):
    __slots__ = ("length", "element_type")

    def __init__(self, length, element_type):
        super().__init__()
        self.length = length
        self.element_type = element_type

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.length!r}, {self.element_type!r})".format(
                cls=type(self), self=self
            )

    def encode(self):
        return "{}{}{}{}".format(
            _C_ARY_B,
            self.length, self.element_type.encode(),
            _C_ARY_E
        )


class Field(InternalType):
    __slots__ = ("name", "type")

    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.type = type

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.name!r}, {self.type!r})".format(cls=type(self), self=self)

    def encode(self):
        if self.name is None:
            return self.type.encode()
        else:
            return '"{}"{}'.format(self.name, self.type.encode())


class Struct(BaseType):
    __slots__ = ("name", "fields")

    def __init__(self, name, fields):
        super().__init__()
        self.name = name
        self.fields = fields

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.name!r}, {self.fields!r})".format(
                cls=type(self), self=self
            )

    def encode(self):
        name = _C_UNDEF if self.name is None else self.name

        if self.fields is None:
            return "{}{}{}".format(_C_STRUCT_B, name, _C_STRUCT_E)
        else:
            return "{}{}={}{}".format(
                _C_STRUCT_B,
                name, "".join(field.encode() for field in self.fields),
                _C_STRUCT_E
            )


class Union(BaseType):
    __slots__ = ("name", "fields")

    def __init__(self, name, fields):
        super().__init__()
        self.name = name
        self.fields = fields

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}" \
            "({self.name!r}, {self.fields!r})".format(
                cls=type(self), self=self
            )

    def encode(self):
        name = _C_UNDEF if self.name is None else self.name

        if self.fields is None:
            return "{}{}{}".format(_C_UNION_B, name, _C_UNION_E)
        else:
            return "{}{}={}{}".format(
                _C_UNION_B,
                name, "".join(field.encode() for field in self.fields),
                _C_UNION_E
            )


class QualifiedType(BaseType):
    __slots__ = (
        "type", "const", "in_", "inout", "out", "bycopy", "byref", "oneway"
    )

    def __init__(self, type, *, const=False, in_=False, inout=False,
                 out=False, bycopy=False, byref=False, oneway=False):
        super().__init__()
        self.type = type
        self.const = const
        self.in_ = in_
        self.inout = inout
        self.out = out
        self.bycopy = bycopy
        self.byref = byref
        self.oneway = oneway

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}(" \
            "type={self.type!r}, const={self.const!r}, " \
            "in_={self.in_!r}, inout={self.inout!r}, out={self.out!r}, " \
            "bycopy={self.bycopy!r}, byref={self.byref!r}, " \
            "oneway={self.oneway!r})".format(cls=type(self), self=self)


class Property(object):
    __slots__ = (
        "type",
        "name",
        "readonly",
        "copy",
        "retain",
        "nonatomic",
        "getter",
        "setter",
        "dynamic",
        "weak",
        "gc",
        "old_encoding",
    )

    def __init__(
            self,
            type,
            name,
            *,
            readonly=False,
            copy=False,
            retain=False,
            nonatomic=False,
            getter=None,
            setter=None,
            dynamic=False,
            weak=False,
            gc=False,
            old_encoding=None
    ):
        super().__init__()
        self.type = type
        self.name = name
        self.readonly = readonly
        self.copy = copy
        self.retain = retain
        self.nonatomic = nonatomic
        self.getter = getter
        self.setter = setter
        self.dynamic = dynamic
        self.weak = weak
        self.gc = gc
        self.old_encoding = old_encoding

    def __repr__(self):
        return "{cls.__module__}.{cls.__qualname__}(type={self.type!r}, " \
            "name={self.name!r}, readonly={self.readonly!r}, " \
            "copy={self.copy!r}, retain={self.retain!r}, " \
            "nonatomic={self.nonatomic!r}, getter={self.getter!r}, " \
            "setter={self.setter!r}, dynamic={self.dynamic!r}, " \
            "weak={self.weak!r}, gc={self.gc!r}, " \
            "old_encoding={self.old_encoding!r})".format(
                cls=type(self), self=self
            )

# Map for simple (single-character) type encodings.
_TYPE_ENCODING_MAP = {
    _C_CLASS: CLASS,
    _C_SEL: SELECTOR,
    _C_CHR: SIGNED_CHAR,
    _C_UCHR: UNSIGNED_CHAR,
    _C_SHT: SHORT,
    _C_USHT: UNSIGNED_SHORT,
    _C_INT: INT,
    _C_UINT: UNSIGNED_INT,
    _C_LNG: LONG,
    _C_ULNG: UNSIGNED_LONG,
    _C_LNG_LNG: LONG_LONG,
    _C_ULNG_LNG: UNSIGNED_LONG_LONG,
    _C_FLT: FLOAT,
    _C_DBL: DOUBLE,
    _C_BOOL: BOOL,
    _C_VOID: VOID,
    _C_UNDEF: UNKNOWN_TYPE,
    _C_CHARPTR: Pointer(CHAR),
}

_decode_cache = {}


def _decode_internal(enc, pos):
    """Decode the start of the given type encoding and return a tuple
    (tp, used) containinc the decoded type and the number of characters
    "consumed". Raise a ValueError if the encoding is not valid.

    If enc is a substring of a longer type encoding, pos should be enc's
    position in the source string, and 0 otherwise.
    (This value is only used in error messages.)
    """

    if not enc:
        raise ValueError("EOL while decoding (position {})".format(pos))

    try:
        return _TYPE_ENCODING_MAP[enc[0]], 1
    except KeyError:
        if enc[0] == _C_PTR:
            tp, used = _decode_internal(enc[1:], pos + 1)
            return Pointer(tp), used + 1
        elif enc[0] == _C_ID:
            if len(enc) > 1 and enc[1] == '"':
                name, sep, after = enc[2:].partition('"')
                if not sep:
                    raise ValueError("EOL while decoding "
                                     "object class name (position {})".format(
                                         pos))
                return ID(name), len(name) + 3
            elif len(enc) > 1 and enc[1] == "?":
                return ID(None), 2
            else:
                return ID(None), 1
        elif enc[0] == _C_BFLD:
            i = 1
            while i < len(enc) and enc[i] in "0123456789":
                i += 1

            if i == 1:
                raise ValueError("EOL while decoding "
                                 "bit field (position {})".format(
                                     pos))

            return BitField(int(enc[1:i])), i
        elif enc[0] == _C_ARY_B:
            i = 1
            while i < len(enc) and enc[i] in "0123456789":
                i += 1

            if i == 1:
                raise ValueError("Missing length in array "
                                 "(position {})".format(pos))

            tp, used = _decode_internal(enc[i:], pos + i)

            if enc[i + used] != _C_ARY_E:
                raise ValueError("Expected end of array "
                                 "(position {})".format(pos + i + used))

            return Array(int(enc[1:i]), tp), i + used + 1
        elif enc[0] in (_C_UNION_B, _C_STRUCT_B):
            if enc[0] == _C_UNION_B:
                cls = Union
                end = _C_UNION_E
            else:
                cls = Struct
                end = _C_STRUCT_E

            eq_pos = enc.find("=", 1, -1)
            end_pos = enc.find(end, 1)

            if end_pos == -1:
                raise ValueError("EOL while decoding struct or "
                                 "union name (position {})".format(pos + 1))
            else:
                if eq_pos == -1:
                    name_end = end_pos
                else:
                    name_end = eq_pos

            name = enc[1:name_end]
            if name == "?":
                name = None

            if eq_pos == -1:
                return cls(name, None), name_end + 1

            i = eq_pos + 1

            fields = []
            while enc[i] != end:
                field_name = None
                if enc[i] == '"':
                    end_quote_pos = enc.find('"', i + 1)
                    if end_quote_pos == -1:
                        raise ValueError("EOL while decoding struct or union "
                                         "field name (position {})".format(
                                             pos + i))

                    field_name = enc[i + 1:end_quote_pos]
                    i = end_quote_pos + 1

                tp, used = _decode_internal(enc[i:], pos + i)
                fields.append(Field(field_name, tp))
                i += used

            return cls(name, fields), i + 1
        else:
            raise ValueError("Invalid start of encoding: "
                             "{!r} (position {})".format(enc[0], pos))


def _decode_qualified_internal(enc, pos):
    """Decode the start of enc, like _decode_internal, except that type
    qualifiers (as found in some method signatures) are recognized.
    The result is returned as a QualifiedType."""

    seen_qualifiers = set()
    kwargs = {}

    for i, char in enumerate(enc):
        if char in seen_qualifiers:
            raise ValueError("Qualifier {} appeared more than once "
                             "(position {})".format(pos + i))

        seen_qualifiers.add(char)

        if char == "r":
            kwargs["const"] = True
        elif char == "n":
            kwargs["in_"] = True
        elif char == "N":
            kwargs["inout"] = True
        elif char == "o":
            kwargs["out"] = True
        elif char == "O":
            kwargs["bycopy"] = True
        elif char == "R":
            kwargs["byref"] = True
        elif char == "V":
            kwargs["oneway"] = True
        else:
            break

    tp, used = _decode_internal(enc[i:], pos + i)
    return QualifiedType(tp, **kwargs), i + used


@functools.lru_cache()
def decode(enc):
    """Decode the given type encoding into an instance of the appropriate
    BaseType subclass.

    If the encoding is empty, invalid or contains multiple types, raise a
    ValueError.
    """

    tp, used = _decode_internal(enc, 0)
    if used < len(enc):
        raise ValueError("Encoding contains more than one type "
                         "({} characters remaining)".format(len(enc) - used))
    return tp


@functools.lru_cache()
def decode_method_signature(enc):
    """Decode the given method signature (i. e. the type encodings for the
    return type and all argument types concatenated) into a tuple
    (restype, argtypes).

    restype is the method return type (the first type encoding)
    as a QualifiedType.
    argtypes is a list of all argument types (all remaining type encodings,
    if any), each as a QualifiedType.

    If the encoding is empty or invalid, raise a ValueError.
    """

    restype, i = _decode_qualified_internal(enc, 0)
    while i < len(enc) and enc[i] in "0123456789":
        i += 1

    argtypes = []
    while i < len(enc):
        argtype, used = _decode_qualified_internal(enc[i:], i)
        argtypes.append(argtype)
        i += used

        while i < len(enc) and enc[i] in "0123456789":
            i += 1

    return restype, argtypes


@functools.lru_cache()
def decode_property(enc):
    """Decode the given property type encoding into a Property instance.

    If the encoding is missing the T or V part or is otherwise invalid,
    raise a ValueError.
    """

    if not enc:
        raise ValueError("Encoding is empty")

    parts = enc.split(",")
    seen_parts = set()
    kwargs = {}

    for i, part in enumerate(parts):
        if not part:
            raise ValueError("Encoding part at index {} is empty".format(i))

        part_id, part_args = part[0], part[1:]

        if part_id in seen_parts:
            raise ValueError("Part {} (index {}) is present more "
                             "than once".format(part[0], i))

        seen_parts.add(part_id)

        if part_id == "T":
            if i != 0:
                raise ValueError("Part T must be at index 0, not {}".format(i))

            kwargs["type"] = decode(part_args)
        elif part_id == "V":
            if i != len(parts) - 1:
                raise ValueError("Part V must be at the last "
                                 "index ({}), not {}".format(
                                     len(parts) - 1, i))

            kwargs["name"] = part_args
        elif part_id == "R":
            if len(part) != 1:
                raise ValueError("Part R takes no arguments")

            kwargs["readonly"] = True
        elif part_id == "C":
            if len(part) != 1:
                raise ValueError("Part C takes no arguments")

            kwargs["copy"] = True
        elif part_id == "&":
            if len(part) != 1:
                raise ValueError("Part & takes no arguments")

            kwargs["retain"] = True
        elif part_id == "N":
            if len(part) != 1:
                raise ValueError("Part N takes no arguments")

            kwargs["nonatomic"] = True
        elif part_id == "G":
            kwargs["getter"] = part_args
        elif part_id == "S":
            kwargs["setter"] = part_args
        elif part_id == "D":
            if len(part) != 1:
                raise ValueError("Part D takes no arguments")

            kwargs["dynamic"] = True
        elif part_id == "W":
            if len(part) != 1:
                raise ValueError("Part W takes no arguments")

            kwargs["weak"] = True
        elif part_id == "P":
            if len(part) != 1:
                raise ValueError("Part P takes no arguments")

            kwargs["gc"] = True
        elif part_id == "t":
            kwargs["old_encoding"] = part_args
        else:
            raise ValueError("Unknown part {} (index {})".format(
                part_id, i
            ))

    if "type" not in kwargs:
        raise ValueError("The T part is required")
    elif "name" not in kwargs:
        raise ValueError("The V part is required")

    return Property(**kwargs)


def encode(tp):
    return tp.encode()

_SCALAR_TYPE_MAP = {
    "char": ctypes.c_char,
    "signed char": ctypes.c_byte,
    "unsigned char": ctypes.c_ubyte,
    "short": ctypes.c_short,
    "unsigned short": ctypes.c_ushort,
    "int": ctypes.c_int,
    "unsigned int": ctypes.c_uint,
    "long": ctypes.c_long,
    "unsigned long": ctypes.c_ulong,
    "long long": ctypes.c_longlong,
    "unsigned long long": ctypes.c_ulonglong,
    "float": ctypes.c_float,
    "double": ctypes.c_double,
    "bool": ctypes.c_bool,
}


class UnknownType(ctypes.Structure):
    _fields_ = []


class UnknownStruct(ctypes.Structure):
    _fields_ = []


class UnknownUnion(ctypes.Structure):
    _fields_ = []


def _encoding_type_to_ctypes(tp):
    if not isinstance(tp, BaseType):
        raise TypeError(
            "tp must be an instance of a objc.encoding.BaseType "
            "subclass"
        )

    if isinstance(tp, InternalType):
        raise TypeError(
            "Internal types (e. g. fields and bit fields) cannot be"
            " converted to ctypes directly"
        )

    if isinstance(tp, QualifiedType):
        return _encoding_type_to_ctypes(tp.type)
    elif isinstance(tp, UnknownType):
        return UnknownType
    elif isinstance(tp, Void):
        return None
    elif isinstance(tp, Scalar):
        return _SCALAR_TYPE_MAP[tp.type]
    elif isinstance(tp, Pointer):
        return ctypes.POINTER(_encoding_type_to_ctypes(tp.element_type))
    elif isinstance(tp, ID):
        return ctypes.c_void_p
    elif isinstance(tp, Class):
        return ctypes.c_void_p
    elif isinstance(tp, Selector):
        return ctypes.c_void_p
    elif isinstance(tp, Array):
        return _encoding_type_to_ctypes(tp.element_type) * tp.length
    elif isinstance(tp, (Struct, Union)):
        if tp.name is None and tp.fields is None:
            return UnknownStruct if isinstance(tp, Struct) else UnknownUnion

        base = ctypes.Structure if isinstance(tp, Struct) else ctypes.Union

        name = "Anonymous" if tp.name is None else tp.name

        if tp.name == 'CGRect':
            return CoreGraphics.CGRect
        if tp.name == 'CGPoint':
            return CoreGraphics.CGPoint
        if tp.name == 'CGSize':
            return CoreGraphics.CGSize
        if tp.name == 'CGAfflineTransform':
            return CoreGraphics.CGAfflineTransform
        if tp.name == 'CGVector':
            return CoreGraphics.CGVector
        if tp.name == 'NSRange' or tp.name == '_NSRange':
            return Foundation.NSRange

        if tp.fields is None:
            return type(name, (base,), {"_fields_": []})
        else:
            fields = []
            for i, field in enumerate(tp.fields):
                field_name = "_field_{}".format(i) if field.name is \
                    None else field.name
                if isinstance(field.type, BitField):
                    if field.type.width == 1:
                        field_decl = (ctypes.c_bool, field_name, 1)
                    else:
                        field_decl = (
                            ctypes.c_uint, field_name, field.type.width
                        )
                else:
                    field_decl = (
                        field_name, _encoding_type_to_ctypes(field.type)
                    )
                fields.append(field_decl)

            return type(name, (base,), {"_fields_": fields})


def decode_method(signature=None, restype=None, argtypes=None):
    if argtypes is None and restype is None:
        restype, argtypes = decode_method_signature(signature)
    restype = _encoding_type_to_ctypes(restype)
    argtypes = [_encoding_type_to_ctypes(x) for x in argtypes]
    return restype, argtypes


def decode_prop(signature):
    property = decode_property(signature)
    return _encoding_type_to_ctypes(property)


def decode_ivar(typeencoding):
    ivar = decode(typeencoding)
    return _encoding_type_to_ctypes(ivar)

__all__ = [
    'decode', 'decode_method', 'decode_prop', 'decode_method_signature',
    'decode_ivar'
]


def main():
    restype, argtypes = decode_method('{CGRect={CGPoint=dd}{CGSize=dd}}@:'
                                      '{CGRect={CGPoint=dd}{CGSize=dd}}'
                                      '{CGPoint=dd}')
    print(restype._fields_)
    print(restype, argtypes)

if __name__ == '__main__':
    main()

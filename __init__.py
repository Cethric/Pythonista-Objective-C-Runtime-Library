from ctypes import (
    CFUNCTYPE, c_uint, byref, POINTER, c_void_p, c_char_p, c_int, py_object
)
import os
import sys

for obj in sys.meta_path:
    if (type(obj).__module__ == "objc" or
        type(obj).__module__ == "__main__") and \
            type(obj).__name__ == "_ObjCSpecialFinderLoader":
        sys.meta_path.remove(obj)
        break
del obj

try:
    from _functions import (
        sel_registerName, sel_getName, sel_isEqual, objc_getClass,
        objc_allocateClassPair, class_addMethod, objc_registerClassPair,
        objc_getMetaClass, class_getName, class_getSuperclass,
        class_isMetaClass, class_copyMethodList, free, method_getName,
        class_getClassMethod, method_getTypeEncoding, objc_msgSend,
        object_getClass, class_copyPropertyList, property_getName,
        class_getInstanceMethod, objc_msgSendSuper, NSGetSizeAndAlignment,
        class_addIvar, objc_getProtocol, class_addProtocol, c,
        object_getClassName, protocol_conformsToProtocol, class_copyIvarList,
        ivar_getName, ivar_getTypeEncoding, object_getIvar, object_setIvar,
        objc_getClassList
    )
except ImportError:
    from ._functions import (
        sel_registerName, sel_getName, sel_isEqual, objc_getClass,
        objc_allocateClassPair, class_addMethod, objc_registerClassPair,
        objc_getMetaClass, class_getName, class_getSuperclass,
        class_isMetaClass, class_copyMethodList, free, method_getName,
        class_getClassMethod, method_getTypeEncoding, objc_msgSend,
        object_getClass, class_copyPropertyList, property_getName,
        class_getInstanceMethod, objc_msgSendSuper, NSGetSizeAndAlignment,
        class_addIvar, objc_getProtocol, class_addProtocol, c,
        object_getClassName, protocol_conformsToProtocol, class_copyIvarList,
        ivar_getName, ivar_getTypeEncoding, object_getIvar, object_setIvar,
        objc_getClassList
    )

try:
    from _structures import (
        objc_super_struct
    )
except ImportError:
    from ._structures import (
        objc_super_struct
    )


try:
    from objc_encoding import (
        decode_method, decode_method_signature, decode_ivar
    )
except ImportError as e:
    from .objc_encoding import (
        decode_method, decode_method_signature, decode_ivar
    )

try:
    from blocks import _ObjCBlock
except ImportError:
    from .blocks import _ObjCBlock


DEBUG = False

oldf = open('nslog.txt', 'w')
oldfd = oldf.fileno()
newfd = sys.__stderr__.fileno()
os.close(newfd)
os.dup2(oldfd, newfd)


class SEL(object):
    _cached_selectors = {}

    def __init__(self, selectorNameOrID):
        if isinstance(selectorNameOrID, (c_void_p, int)):
            sel_str = sel_getName(selectorNameOrID)
            if sel_str in self._cached_selectors:
                self.sel = self._cached_selectors[sel_str]
            else:
                self.sel = selectorNameOrID
                self._cached_selectors[sel_str] = self.sel
        else:
            if isinstance(selectorNameOrID, bytes):
                sel_str = selectorNameOrID
            else:
                sel_str = selectorNameOrID.encode()

            if sel_str in self._cached_selectors:
                self.sel = self._cached_selectors[sel_str]
            else:
                self.sel = sel_registerName(sel_str)
                self._cached_selectors[sel_str] = self.sel
        self._as_parameter_ = self.sel

    def __str__(self):
        if self.sel:
            name = sel_getName(self.sel).decode()
        else:
            name = ""
        return "<SEL.{} object at 0x{}>".format(name, id(self))

    def __eq__(self, other):
        result = False
        if isinstance(other, SEL):
            result = sel_isEqual(self.sel, other.sel)
        else:
            raise ValueError(
                "'{}' must be of type SEL, not '{}'".format(
                    other, type(other)
                )
            )
        return result

methodIgnores = [
    '__weakref__', 'class_methods', '__new__', '__module__',
    '__init__', '__doc__', '__call__', 'name', '__dict__', 'instance_methods',
    '_ptr', '__qualname__', '__protocols__'
]

_cached_instances = {}
_cached_method_list = {}
_cached_instance_method_calls = {}
_cached_overrides = {}


class _ObjCInstance(object):
    NSString = None

    def __new__(cls, ptr, klass):
        ptr = getattr(ptr, '_objc_ptr', None) or ptr
        if ptr in _cached_instances:
            return _cached_instances[ptr]
        self = super().__new__(cls)
        self.name = ""
        self._instance = ptr
        self._as_parameter_ = self._instance
        self._ptr = object_getClass(ptr)
        _cached_instances[ptr] = self
        self.klass = klass
        if self.NSString is None:
            self.NSString = findClass("NSString")()
        return self

    def __init__(self, ptr, klass):
        if self._ptr in _cached_method_list:
            self._methods = _cached_method_list[self._ptr]
        else:
            self._methods = get_instance_method_names(self)
            _cached_method_list[self._ptr] = self._methods
        self.overrides = getattr(klass, 'overrides', {})
        _cached_overrides[self] = self.overrides
        self._ivars = get_ivars(self)
        self._properties = get_properties(self)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            cname = "{}.{}".format(self._instance, name)
            if cname in _cached_instance_method_calls:
                return _cached_instance_method_calls[cname]

            if name in _cached_overrides[self]:
                m = _cached_overrides[self][name]
                if hasattr(m, 'instance'):
                    m.instance = self.klass
                _cached_instance_method_calls[cname] = m
                return m

            if name in self._ivars:
                # print(
                #     "Get Instance Variable: {} for {} {}".format(
                #         name, self, self._ivars[name]
                #     )
                # )
                typeptr = ivar_getTypeEncoding(self._ivars[name])
                object_getIvar.restype = decode_ivar(typeptr.decode())
                p = object_getIvar(self._instance, self._ivars[name])
                if typeptr == '@':
                    p = _ObjCInstance(p, None)
                # _cached_instance_method_calls[cname] = p
                return p

            if name in self._properties:
                getter = self._properties[name].getter
                if getter in self._methods:
                    m = self._methods[name]
                    return _ObjCInstanceMethod(self, m)()

            if name in self._methods:
                m = self._methods[name]
                m = _ObjCInstanceMethod(self, m)
                _cached_instance_method_calls[cname] = m
                return m
        # print(name, name in self._methods)
        raise AttributeError("Cannot find attribute '{}'".format(name))

    def __setattr__(self, name, value):
        if '_properties' in self.__dict__:
            if name in self._ivars:
                typeptr = ivar_getTypeEncoding(self._ivars[name])
                object_setIvar.argtypes = [
                    c_void_p, c_void_p, decode_ivar(typeptr.decode())
                ]
                # print(
                #     "Set Instance Variable: {} for {} {}".format(
                #         name, self, self._ivars[name]
                #     )
                # )
                object_setIvar(self._instance, self._ivars[name], value)
                return
            if name in self._properties:
                setter = self._properties[name].setter
                if setter in self._methods:
                    m = self._methods[setter]
                    _ObjCInstanceMethod(self, m)(value)
                    return
                else:
                    raise AttributeError(
                        "The setter {} is not valid for '{}'".format(
                            setter, name
                        )
                    )
        super().__setattr__(name, value)

    def __dir__(self):
        d = list(super().__dir__())
        return d + list(self._methods)

    def __str__(self):
        objc_msgSend.argtypes = [c_void_p, c_void_p]
        objc_msgSend.restype = c_void_p
        desc = objc_msgSend(
            self._instance,
            SEL("description")
        )

        objc_msgSend.argtypes = [c_void_p, c_void_p]
        objc_msgSend.restype = c_char_p
        desc_str = objc_msgSend(
            desc,
            SEL("cString")
        )
        if desc_str is None:
            return 'None'
        try:
            return desc_str.decode()
        except UnicodeDecodeError:
            return desc_str.decode('utf8', 'replace')

    def __getitem__(self, name):
        if 'valueForKey_' not in self._methods:
            raise RuntimeError(
                "{} does not conform to 'NSKeyValueCoding' protocol".format(
                    self
                )
            )
        m = self._methods['valueForKey_']
        n = self.NSString.alloc().initWithUTF8String_(name.encode())
        v = _ObjCInstanceMethod(self, m)(n)
        return v

    def __setitem__(self, name, value):
        if 'setValue_forKey_' not in self._methods:
            raise RuntimeError(
                "{} does not conform to 'NSKeyValueCoding' protocol".format(
                    self
                )
            )
        m = self._methods['setValue_forKey_']
        NSString = findClass("NSString")()
        n = NSString.alloc().initWithUTF8String_(name.encode())
        _ObjCInstanceMethod(self, m)(value, n)


class _ObjCInstanceMethod(object):
    def __init__(self, klass, sel_name):
        self.sel_name = sel_name
        self.sel = SEL(sel_name)
        self.class_ptr = klass._ptr
        self.klass = klass
        self.instance_ptr = klass._instance
        self.method = class_getInstanceMethod(self.class_ptr, self.sel)
        self._objc_msgSend = None

        signature = method_getTypeEncoding(self.method).decode()
        self.restype, self.argtypes = decode_method_signature(signature)

    def __call__(self, *args):
        if self._objc_msgSend is None:
            self._objc_msgSend = objc_msgSend
        restype, argtypes = decode_method(
            argtypes=self.argtypes,
            restype=self.restype
        )
        self._objc_msgSend.restype = restype
        for i, a in enumerate(args):
            if getattr(a, 'invoke', False):
                argtypes[i + 2] = POINTER(a.__class__)
                args[i] = byref(a)
        self._objc_msgSend.argtypes = argtypes
        r = self._objc_msgSend(self.instance_ptr, self.sel, *args)
        if self.restype and self.restype.type.encode() == "@":
            return _ObjCInstance(r, self.klass)
        return r


class _ObjCClassMethod(object):
    def __init__(self, klass, sel_name):
        self.sel_name = sel_name
        self.sel = SEL(sel_name)
        self.class_ptr = klass._ptr
        self.klass = klass
        self.method = class_getClassMethod(self.class_ptr, self.sel)
        self._objc_msgSend = None

        self.sig = method_getTypeEncoding(self.method).decode()
        self.restype, self.argtypes = decode_method_signature(self.sig)
        self.crestype, self.cargtypes = decode_method(
            argtypes=self.argtypes,
            restype=self.restype
        )

    def __call__(self, *args):
        if self._objc_msgSend is None:
            self._objc_msgSend = objc_msgSend

        self._objc_msgSend.restype = self.crestype
        args = list(args)
        for i, a in enumerate(args):
            if getattr(a, 'invoke', False):
                print(a.__class__)
                self.cargtypes[i + 2] = POINTER(a.__class__)
                print("Block")
                args[i] = byref(a)
        self._objc_msgSend.argtypes = self.cargtypes

        r = self._objc_msgSend(self.class_ptr, self.sel, *args)
        if self.restype and self.restype.type.encode() == "@":
            return _ObjCInstance(r, self.klass)
        return r

_cached_supers = {}


def get_class_supers(klass):
    if klass._ptr in _cached_supers:
        return _cached_supers[klass._ptr]
    supers = [klass._ptr]
    cls_pointer = klass._ptr
    while True:
        cls_pointer = class_getSuperclass(cls_pointer)
        if cls_pointer is None:
            break
        supers.append(cls_pointer)
    _cached_supers[klass._ptr] = supers
    return supers

_cached_ivars = {}
_cached_properties = {}


def get_ivars(klass):
    if klass._instance in _cached_ivars:
        return _cached_ivars[klass._instance]
    supers = [klass._ptr]  # get_class_supers(klass)[:0]
    properties = {}

    for cls_pointer in supers:
        icount = c_uint(0)
        class_copyIvarList(cls_pointer, byref(icount))
        res = POINTER(c_void_p * icount.value)
        class_copyIvarList.restype = res
        r = class_copyIvarList(cls_pointer, None)
        if icount.value > 0:
            for prop in r.contents:
                if prop is None:
                    continue
                n = ivar_getName(prop).decode()
                properties[n] = prop
        free.argtypes = [res]
        free(r)
    del supers
    _cached_ivars[klass._ptr] = properties
    return properties


class _Property(object):
    def __init__(self, ptr, name):
        self.getter = name
        self.setter = self._setter_name(name)

    def _setter_name(self, name):
        if name.startswith('is'):
            name = name[2:]
        if name.startswith('get'):
            name = name[3:]
        name = name[0].upper() + name[1:]
        name = "set{}_".format(name)
        return name


def get_properties(klass):
    if klass._ptr in _cached_properties:
        return _cached_properties[klass._ptr]
    properties = {}
    supers = get_class_supers(klass)

    for cls_pointer in supers:
        icount = c_uint(0)
        class_copyPropertyList(cls_pointer, byref(icount))
        res = POINTER(c_void_p * icount.value)
        class_copyPropertyList.restype = res
        r = class_copyPropertyList(cls_pointer, None)
        if icount.value > 0:
            for prop in r.contents:
                if prop is None:
                    continue
                n = property_getName(prop).decode()
                properties[n] = _Property(prop, n)
        free.argtypes = [res]
        free(r)
    del supers
    _cached_properties[klass._ptr] = properties
    return properties

_cached_instance_methods = {}
_cached_super_instance_methods = {}
_cached_class_methods = {}


def get_instance_method_names(klass):
    if klass._ptr in _cached_instance_methods:
        return _cached_instance_methods[klass._ptr]
    methods = {}
    supers = get_class_supers(klass)
    for cls_pointer in supers:
        if cls_pointer in _cached_super_instance_methods:
            # methods.extend([
            #     n for n in _cached_super_instance_methods[cls_pointer]
            #     if n not in methods
            # ])
            methods.update(_cached_super_instance_methods[cls_pointer])
        else:
            method_num = c_uint()
            class_copyMethodList(cls_pointer, byref(method_num))
            class_copyMethodList.restype = POINTER(c_void_p * method_num.value)
            methodList = class_copyMethodList(cls_pointer, None)
            if method_num.value > 0:
                super_methods = {}
                for method in methodList.contents:
                    name = method_getName(method).decode()
                    # super_methods.append(name)
                    super_methods[name.replace(":", "_")] = name
                    if name not in methods:
                        # methods.append(name)
                        methods[name.replace(":", "_")] = name
                _cached_super_instance_methods[cls_pointer] = super_methods
            free.argtypes = [class_copyMethodList.restype]
            free(methodList)
    _cached_instance_methods[klass._ptr] = methods
    return methods


def get_class_method_names(klass):
    if klass._ptr in _cached_class_methods:
        return _cached_class_methods[klass._ptr]
    methods = []
    supers = get_class_supers(klass)

    for cls_pointer in supers:
        meta = objc_getMetaClass(class_getName(cls_pointer))
        if meta in _cached_class_methods:
            methods.extend(_cached_class_methods[meta])
        else:
            if class_isMetaClass(meta):
                method_num = c_uint()
                class_copyMethodList(meta, byref(method_num))
                class_copyMethodList.restype = POINTER(
                    c_void_p * method_num.value
                )
                methodList = class_copyMethodList(meta, None)
                super_methods = []
                if method_num.value > 0:
                    for method in methodList.contents:
                        name = method_getName(method).decode()
                        super_methods.append(name)
                        if name not in methods:
                            methods.append(name)
                    _cached_instance_methods[meta] = super_methods
                free.argtypes = [class_copyMethodList.restype]
                free(methodList)
            else:
                raise RuntimeError("Could not find the MetaClass for "
                                   "'{}'".format(
                                       class_getName(cls_pointer)
                                   ))
    _cached_class_methods[klass._ptr] = methods
    return methods

_cached_class_method_list = {}


class _ObjCClass(object):
    def __init__(self, wrapper):
        self.name = wrapper.name
        self._ptr = wrapper._ptr
        self._protocols = wrapper.__protocols__
        self.overrides = getattr(wrapper, 'overrides', {})
        self._objc_method_names = get_class_method_names(self)
        if self._ptr in _cached_class_method_list:
            self._methods = _cached_class_method_list[self._ptr]
        else:
            self._methods = {
                x.replace(":", "_"): x for x in self._objc_method_names
            }
            _cached_class_method_list[self._ptr] = self._methods

    def __getattr__(self, name):
        if name in self.overrides:
            # print("Overrided Function")
            m = self.overrides[name]
            if hasattr(m, 'instance'):
                m.instance = self.klass
            return m
        if name in self._methods:
            m = self._methods[name]
            return _ObjCClassMethod(self, m)
        return super().__getattr__(name)

    def __repr__(self):
        return "<__main__.{} object at 0x{}>".format(self.name, id(self))

    def __dir__(self):
        d = list(super().__dir__())
        return d + list(self._methods)


class _ObjCClassType(type):
    __protocols__ = []

    def __init__(self, *args, **kwargs):
        self.name = ""
        if len(args) == 4:
            metaclass, name, bases, namespace = args
            self.name = name
            super().__init__(metaclass, name, bases, namespace)
        elif len(args) == 3:
            name, base, namespace = args
            self.name = name
            super().__init__(name, base, namespace)
        elif len(args) == 2:
            super().__init__(self)
            self.name = args[0]
            self._ptr = args[1]
        else:
            super().__init__(self)
            self.name = self.__name__
            print(self.name)

    def __new__(*args, **kwargs):
        if len(args) == 4:
            metaclass, name, bases, namespace = args
            klass = super(_ObjCClassType, metaclass).__new__(
                metaclass, name, bases, namespace
            )
            # print("Creating New ObjC Object")
            # print("Name: {}".format(name))
            # print("Super: {}".format(class_getName(klass._ptr).decode()))
            # print("Protocols: {}".format(klass.__protocols__))
            i = 0
            basename = name
            while True:
                if objc_getClass(name.encode()) is not None:
                    i += 1
                    name = "{}_{}".format(basename, i)
                else:
                    break
            klass.name = name
            new_klass = objc_allocateClassPair(bases[0]._ptr, name.encode(), 0)

            for proto in klass.__protocols__:
                if getattr(proto, '_ptr', None):
                    protocol = proto._ptr
                else:
                    protocol = objc_getProtocol(proto.encode())
                if protocol is None:
                    raise RuntimeError(
                        "Can not find protocol '{}' for class '{}'".format(
                            getattr(proto, 'name', proto),
                            name
                        )
                    )
                class_addProtocol(new_klass, protocol)

            names = []

            for k, v in namespace.items():
                if k in methodIgnores:
                    continue
                if getattr(v, '_property', False):
                    status = class_addIvar(
                        new_klass,
                        k.encode(),
                        v.sizep,
                        v.alignp,
                        v._typeEncoding.encode()
                    )
                    if DEBUG:
                        print("Adding Property {} {}".format(k, status))
                    names.append(k)
                    continue

                if not getattr(v, '_instanceMethod', False):
                    continue
                if any([getattr(p, k, False) for p in klass.__protocols__]):
                    c = False
                    for p in [getattr(
                            p, k, None
                    ) for p in klass.__protocols__]:
                        if p is None:
                            continue
                        c = p._instanceMethod
                    if not c:
                        continue
                if getattr(v, '_objc_super', None) is not None:
                    class_addMethod.argtypes = [
                        c_void_p, c_void_p, v._cFuncType, c_char_p
                    ]
                    class_addMethod(
                        new_klass,
                        SEL(v._funcname),
                        v._cFunc,
                        (v._restype + "".join(v._argtypes)).encode()
                    )
                    names.append(k)
                    continue
            objc_registerClassPair(new_klass)
            meta_klass = objc_getMetaClass(class_getName(new_klass))
            for k, v in namespace.items():
                if k in methodIgnores:
                    continue
                if getattr(v, '_instanceMethod', True):
                    continue
                if any([getattr(p, k, False) for p in klass.__protocols__]):
                    c = False
                    for p in [getattr(
                            p, k, None
                    ) for p in klass.__protocols__]:
                        if p is None:
                            continue
                        c = p._instanceMethod
                    if c:
                        continue
                if getattr(v, '_objc_super', None) is not None:
                    class_addMethod.argtypes = [
                        c_void_p, c_void_p, v._cFuncType, c_char_p
                    ]
                    class_addMethod(
                        meta_klass,
                        SEL(v._funcname),
                        v._cFunc,
                        (v._restype + "".join(v._argtypes)).encode()
                    )
                    names.append(k)
            klass._ptr = new_klass
            klass.overrides = {}

            class WrappedOverride(object):
                instance = None

                def __init__(self, function):
                    self.func = function

                def __call__(self, *args, **kwargs):
                    self.func(self.instance, *args, **kwargs)

            for n in namespace:
                if n in methodIgnores:
                    continue
                if n in names:
                    continue
                if callable(namespace[n]):
                    func = WrappedOverride(namespace[n])
                else:
                    func = namespace[n]
                klass.overrides[n] = func

            return klass
        elif len(args) == 3:
            self, name, ptr = args
            klass = super(_ObjCClassType, self).__new__(
                self, name, (object,), dict(self.__dict__)
            )
            # d = dict(self.__dict__)
            klass.name = name
            klass._ptr = ptr
            return klass

    def __call__(self, *args, **kwargs):
        # super().__call__(*args, **kwargs)
        return _ObjCClass(self)


class _ObjCProtocol(object):
    def __init__(self, wrapper):
        self.name = wrapper.name
        self._ptr = wrapper._ptr
        self._as_paramater_ = wrapper._ptr

    def __repr__(self):
        return "<__main__.{} object at 0x{}>".format(self.name, id(self))


class _ObjCProtocolType(type):
    __protocols__ = []

    def __init__(self, *args, **kwargs):
        self.name = None
        if len(args) == 4:
            metaclass, name, bases, namespace = args
            self.name = name
            super().__init__(metaclass, name, bases, namespace)
        elif len(args) == 3:
            name, base, namespace = args
            self.name = name
            super().__init__(name, base, namespace)
        elif len(args) == 2:
            super().__init__(self)
            self.name = args[0]
            self._ptr = args[1]
        else:
            super().__init__(self)
            self.name = self.__name__
            print(self.name)

    def __new__(*args, **kwargs):
        if len(args) == 4:
            metaclass, name, bases, namespace = args
            klass = super(_ObjCProtocolType, metaclass).__new__(
                metaclass, name, bases, namespace
            )
            i = 0
            basename = name
            while True:
                if objc_getProtocol(name.encode()) is not None:
                    i += 1
                    name = "{}_{}".format(basename, i)
                else:
                    break
            # print("Creating New ObjC Protocol")
            # print("Name: {}".format(name))
            # print("Protocols: {}".format(klass.__protocols__))

            new_klass = objc_allocateProtocol(name.encode())
            # class_addProtocol(new_klass, klass._ptr)

            for proto in klass.__protocols__:
                if getattr(proto, '_ptr', None):
                    protocol = proto._ptr
                else:
                    protocol = objc_getProtocol(proto.encode())
                if protocol is None:
                    raise RuntimeError(
                        "Can not find protocol '{}' for class '{}'".format(
                            getattr(proto, 'name', proto),
                            name
                        )
                    )
                print("Adding protocol: {}".format(proto.name))
                class_addProtocol(new_klass, protocol)

            for k, v in namespace.items():
                if k in methodIgnores:
                    continue
                if getattr(v, '_objc_super', None) is not None:
                    protocol_addMethodDescription(
                        new_klass,
                        SEL(v._funcname),
                        (v._restype + "".join(v._argtypes)).encode(),
                        v._requiredMethod,
                        v._instanceMethod,
                    )

            objc_registerProtocol(new_klass)
            klass._ptr = new_klass
            return klass
        elif len(args) == 3:
            self, name, ptr = args
            klass = super(_ObjCProtocolType, self).__new__(
                self, name, (object,), dict(self.__dict__)
            )
            # d = dict(self.__dict__)
            klass.name = name
            klass._ptr = ptr
            return klass

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        return _ObjCProtocol(self)


def get_super_struct(objc_object):
    spr = class_getSuperclass(object_getClass(objc_object))
    # print(
    #     "Class: {}, Superclass: {}".format(
    #         object_getClassName(objc_object), class_getName(spr)
    #     )
    # )
    struct = objc_super_struct(objc_object, spr)
    return struct


def objc_super(_self, _sel, *args, **kwargs):
    signature = getattr(kwargs, "signature", "@")
    restype, argtypes = decode_method_signature(signature)
    restype, argtypes = decode_method(argtypes=argtypes, restype=restype)
    su = get_super_struct(_self)
    argtypes = [POINTER(objc_super_struct), c_void_p]  # + argtypes
    objc_msgSendSuper.argtypes = argtypes
    objc_msgSendSuper.restype = c_void_p  # = restype
    return objc_msgSendSuper(byref(su), _sel)


def objc_protocol_method(
        funcname=None, argtypes=None, restype=None,
        required=False, instanceMethod=True):
    class _Method(object):
        _objc_super = 0
        _funcname = funcname
        _cFunc = None
        _cFuncType = None
        _argtypes = argtypes
        _restype = restype
        _requiredMethod = required
        _instanceMethod = instanceMethod

        def __init__(self, function):
            self.func = function
            if self._funcname is None:
                self._funcname = function.__name__.replace("_", ":")
            if self._restype is None:
                self._restype = function.__annotations__['return'] \
                    if 'return' in function.__annotations__ else 'v'
            if self._argtypes is None:
                a = ['@', ':']
                for k, v in function.__annotations__.items():
                    if k == 'return':
                        continue
                    a.append(v if v else '?')
                self._argtypes = a
            if self._cFunc is None:
                self._signature = self._restype + "".join(self._argtypes)
                restype, argtypes = decode_method_signature(self._signature)
                restype, argtypes = decode_method(
                    argtypes=argtypes,
                    restype=restype
                )
                if self._cFunc is None:
                    self._cFuncType = CFUNCTYPE(
                        restype,
                        *argtypes
                    )
                    self._cFunc = self._cFuncType(self.func)

        def __call__(self, *args, **kwargs):
            print("Function: {}. {} {}".format(self.func, args, kwargs))
            return self.func(*args, **kwargs)

    return _Method


def objc_method(
        funcname=None, argtypes=None, restype=None, instanceMethod=True):
    class _Method(object):
        _objc_super = 0
        _funcname = funcname
        _cFunc = None
        _cFuncType = None
        _argtypes = argtypes
        _restype = restype
        _instanceMethod = instanceMethod

        def __init__(self, function):
            self.func = function
            if self._funcname is None:
                self._funcname = function.__name__.replace("_", ":")
            if self._restype is None:
                self._restype = function.__annotations__['return'] \
                    if 'return' in function.__annotations__ else 'v'
            if self._argtypes is None:
                a = ['@', ':']
                for k, v in function.__annotations__.items():
                    if k == 'return':
                        continue
                    a.append(v if v else '?')
                self._argtypes = a
            self._signature = self._restype + "".join(self._argtypes)
            restype, argtypes = decode_method_signature(self._signature)
            restype, argtypes = decode_method(
                argtypes=argtypes,
                restype=restype
            )

            if self._cFunc is None:
                self._cFuncType = CFUNCTYPE(
                    restype,
                    *argtypes
                )
                self._cFunc = self._cFuncType(self.func)

        def __call__(self, *args, **kwargs):
            print("Function: {}. {} {}".format(self.func, args, kwargs))
            return self.func(*args, **kwargs)

    return _Method


def objc_instanceProperty(typeEncoding):
    class _Property(object):
        _property = True
        _typeEncoding = typeEncoding

        def __init__(self):
            t, self.sizep, self.alignp = NSGetSizeAndAlignment(
                self._typeEncoding
            )
            # print(
            #     "Unchecked: {} Size: {} Alignment: {}".format(
            #         t, self.sizep, self.alignp
            #     )
            # )
            # print(self._typeEncoding)

    return _Property()


def _getClassList():
    r = objc_getClassList(None, 0)
    t = (c_void_p * r)
    objc_getClassList.argtypes = [POINTER(t), c_int]
    a = t()
    objc_getClassList(byref(a), r)
    n = {}
    for i in list(a):
        cn = class_getName(i).decode()
        # if cn.startswith("_"):
        #     continue
        klass = _ObjCClassType(cn, i)
        n[cn] = klass
    return n


_cached_class_list = {}
_cached_protocol_list = {}


def cacheAllClasses():
    global _cached_class_list
    _cached_class_list = _getClassList()


def findClass(className):
    global _cached_class_list
    if className in _cached_class_list:
        return _cached_class_list[className]
    else:
        klass_ptr = objc_getClass(className.encode())
        if klass_ptr:
            klass = _ObjCClassType(className, klass_ptr)
            _cached_class_list[className] = klass
            return klass
    raise ValueError("Cannot Find Class {}".format(className))


def cacheAllProtocols():
    global _cached_protocol_list
    number_protocols = c_uint()
    objc_copyProtocolList(byref(number_protocols))
    ntp = (c_void_p * number_protocols.value)
    objc_copyProtocolList.restype = POINTER(ntp)
    protocols = objc_copyProtocolList(None)
    for protocol in protocols.contents:
        protocol_cls = _ObjCProtocolType(
            protocol_getName(protocol).decode(),
            protocol
        )
        _cached_protocol_list[
            protocol_getName(protocol).decode()
        ] = protocol_cls


def findProtocol(protocolName):
    global _cached_protocol_list
    if protocolName in _cached_protocol_list:
        return _cached_protocol_list[protocolName]
    protocol_ptr = objc_getProtocol(protocolName.encode())
    if protocol_ptr:
        protocol = _ObjCProtocolType(protocolName, protocol_ptr)
        _cached_protocol_list[protocolName] = protocol
        return protocol
    raise ValueError("Can not Find Protocol {}".format(protocolName))


def newKeyCommand(inp, mod, action, title):
    NSString = findClass('NSString')
    UIKeyCommand = findClass('UIKeyCommand')
    i = NSString().alloc().initWithUTF8String_(inp.encode())
    mf = mod
    a = SEL(action)
    t = NSString().alloc().initWithUTF8String_(title.encode())
    k = UIKeyCommand() \
        .keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(
            i, mf, a, t
    )
    return k

# Install the loaders for objc.classes and objc.protocols
# (can only be used once Class and Protocol has been defined, respectively).


class _ClassModuleProxy(type(sys)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._known_names = set()

    def __dir__(self):
        return sorted([*super().__dir__(), *self._known_names])

    def __getattr__(self, name):
        try:
            cls = findClass(name)
        except ValueError as err:
            self._known_names.discard(name)
            raise AttributeError(*err.args)
        else:
            self._known_names.add(name)
            return cls


class _ProtocolModuleProxy(type(sys)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._known_names = set()

    def __dir__(self):
        return sorted([*super().__dir__(), *self._known_names])

    def __getattr__(self, name):
        try:
            proto = findProtocol(name)
        except ValueError as err:
            self._known_names.discard(name)
            raise AttributeError(*err.args)
        else:
            self._known_names.add(name)
            return proto

_MODULE_PROXIES = {
    "objc.classes": _ClassModuleProxy,
    "classes": _ClassModuleProxy,
    "objc.protocols": _ProtocolModuleProxy,
    "protocols": _ProtocolModuleProxy,
}


class _ObjCSpecialFinderLoader(object):
    name = ''
    origin = ''
    has_location = False

    def find_spec(self, fullname, path, *args):
        self.name = fullname
        return self if fullname in _MODULE_PROXIES else None

    def find_module(self, fullname, path=None):
        return self if fullname in _MODULE_PROXIES else None

    def _getLoader(self):
        return self

    loader = property(_getLoader)

    def load_module(self, fullname):
        mod = sys.modules.setdefault(
            fullname,
            _MODULE_PROXIES[fullname](fullname)
        )
        mod.__file__ = "<dynamically created by " \
            "{cls.__module__}.{cls.__name__}>".format(cls=type(self))
        mod.__loader__ = self
        mod.__package__ = "objc"
        mod.__all__ = ["DontEvenTryToStarImportThisModuleYouCrazyPerson"]
        return mod

# Remove old versions of the loader and modules if the objc module is reloaded.

sys.meta_path.append(_ObjCSpecialFinderLoader())
sys.modules.pop("objc.classes", None)
sys.modules.pop("classes", None)
sys.modules.pop("objc.protocols", None)
sys.modules.pop("protocols", None)

s_script = '''
log(9);
throw log
'''


def OBJC(item):
    if isinstance(item, str) or isinstance(item, bytes):
        r = item if isinstance(item, bytes) else item.encode()
        NSString = findClass("NSString")()
        return NSString.alloc().initWithUTF8String_(r)
    if isinstance(item, tuple):
        NSArray = findClass("NSArray")()
        def check(value):
            if isinstance(value, _ObjCInstance):
                return value._ptr
            raise ValueError(
                "Expected _ObjCInstanceType, got '{}'".format(
                    type(value).__name__
                )
            )
        carr = (c_void_p * len(item))(*[i for i in map(check, item)])
        return NSArray.arrayWithObjects_count_(carr, len(item))
    if isinstance(item, list):
        def check(value):
            if isinstance(value, _ObjCInstance):
                return value
            raise ValueError(
                "Expected _ObjCInstanceType, got '{}'".format(
                    type(value).__name__
                )
            )
        ma = findClass("NSMutableArray")().alloc().init()
        [ma.addObject_(i) for i in map(check, item)]
        return ma
    if isinstance(item, (dict)):
        NSDictionary = findClass("NSDictionary")
        keys = (c_void_p * len(item.keys()))(*[OBJC(i)._ptr for i in item.keys()])
        values = (c_void_p * len(item.values()))(*[OBJC(i)._ptr for i in item.values()])
        d = NSDictionary().dictionaryWithObjects_forKeys_count_(
            keys,
            values,
            len(item)
        )
        
        return d
    return _ObjCInstance(item, None)


def main():
    s = SEL('helloWorld_'.encode())
    print(s)
    s2 = SEL('helloWorld2_'.encode())
    print(s2)
    s3 = SEL("helloWorld_")
    print(s3)
    print('selectors are equal?', s == s2, s2 == s3, s == s3)
    
    print(OBJC("TEST"), OBJC("TEST".encode()))
    print(OBJC([OBJC("TEST"), OBJC("TEST2")]))
    print(OBJC((OBJC("TEST"), OBJC("TEST2"))))
    print(OBJC({
        'test': 'a',
        'test2': 'b',
        'test3': 0
    }))
    

    NSObject = findClass('NSObject')

    class Test(NSObject):
        booleanProperty = objc_instanceProperty('B')

        @objc_method()
        def initCustom(_self, _cmd) -> '@':
            result = objc_super(_self, SEL("init"))
            print("init")
            return result

        @objc_method()
        def check(_self, _cmd):
            self = OBJC(_self)
            self.booleanProperty = False
            print("After", self.booleanProperty)

        @objc_method()
        def checkWithValue_(_self, _cmd, _value: 'B'):
            print("Check with value. {}".format(_value))
            self = OBJC(_self)
            self.booleanProperty = _value
            self.check()

    class Test2(Test):

        @objc_method()
        def initCustomWithValue_(_self, _cmd, _value: 'B') -> '@':
            result = objc_super(
                _self, SEL("initCustom"), _value, signature="@B"
            )
            print("initCustomWithValue_")
            OBJC(result).booleanProperty = _value
            print(OBJC(result).booleanProperty)
            return result

        @objc_method()
        def check(_self, _cmd):
            objc_super(_self, _cmd)
            print("Override")

        @objc_method()
        def checkWithValue_(_self, _cmd, _value: 'B'):
            objc_super(_self, _cmd, _value, signature="vB")
            print("Override")

    t = Test().alloc().initCustom()
    t.booleanProperty = True
    print(t.booleanProperty)
    t.check()
    t.checkWithValue_(True)

    t2 = Test2().alloc().initCustomWithValue_(True)
    print(t2.check())
    t2.checkWithValue_(True)

    def blockFunc(
            _self: '@', _cmd: ':',
            arg0: '@"JSValue"', arg1: '@"JSValue"') -> 'v':
        print(arg0, _ObjCInstance(arg1, None))

    def blockFunc2(_self: '@', _cmd: ":", arg0: 'i'):
        print("Hello World,", arg0)

    # block = _ObjCBlock(blockFunc)
    block = _ObjCBlock(blockFunc2)

    JSContext = findClass('JSContext')
    NSString = findClass('NSString')
    JSValue = findClass('JSValue')
    NSMutableArray = findClass('NSMutableArray')

    arguments = NSMutableArray().alloc().init()

    script = NSString().alloc().initWithUTF8String_(s_script.encode())
    name = NSString().alloc().initWithUTF8String_('log'.encode())
    context = JSContext().alloc().init()
    value = JSValue().valueWithObject_inContext_(block.block, context)
    value.callWithArguments_(arguments)
    context.setObject_forKeyedSubscript_(value, name)
    context.evaluateScript_(script)
    exception = context.exception.toObject()
    print(context.exception)
    print(exception)
    # exception.invoke(80)

    # cacheAllClasses()
    # print([x for x in sorted(_cached_class_list.keys()) if '__NS' in x])

if __name__ == '__main__':
    main()

__all__ = [
    'c', 'findClass', '_ObjCInstance', 'cacheAllClasses',
    'objc_method', 'objc_super', 'SEL', 'class_getName',
    'object_getClass', 'object_getClassName', 'findProtocol',
    'objc_protocol_method', 'protocol_conformsToProtocol',
    'objc_instanceProperty', 'newKeyCommand', 'cacheAllProtocols',
    '_ObjCBlock', 'OBJC'
]

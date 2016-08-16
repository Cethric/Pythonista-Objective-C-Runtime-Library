from ctypes import *
import inspect
import types
import pyparsing
import functools
import re
import string
import os
import sys

for obj in sys.meta_path:
    if (type(obj).__module__ == "objc" or type(obj).__module__ == "__main__") and type(obj).__name__ == "_ObjcSpecialFinderLoader":
        sys.meta_path.remove(obj)
        break
del obj

try:
    from _functions import *
except ImportError:
    from ._functions import *

try:
    from CoreGraphics import *
except ImportError:
    from .CoreGraphics import *

try:
    from _structures import *
except ImportError:
    from ._structures import *
    
try:
    from objc_encoding import (
        decode_method, decode, decode_prop, decode_method_signature, decode_ivar
    )
except ImportError as e:
    from .objc_encoding import (
        decode_method, decode, decode_prop, decode_method_signature, decode_ivar
    )
    
    
    
oldf = open('nslog.txt', 'w')
oldfd = oldf.fileno()
newfd = sys.__stderr__.fileno()
os.close(newfd)
os.dup2(oldfd, newfd)

'''
[array type] An array
{name=type...} A structure
(name=type...) A union

type_codes = {
    'c': c_char,
    'B': c_bool,
    'i': c_int,
    's': c_short,
    'l': c_long,
    'q': c_longlong,
    'C': c_ubyte,
    'I': c_uint,
    'S': c_ushort,
    'L': c_ulong,
    'Q': c_ulonglong,
    'f': c_float,
    'd': c_double,
    'v': None,
    '*': c_char_p,
    '@': c_void_p,
    '#': c_void_p,
    ':': c_void_p,
    '?': c_void_p,
    'r*': c_char_p,
    '{CGRect={CGPoint=dd}{CGSize=dd}}': CGRect,
}
'''

methodIgnores = [
    '__weakref__', 'class_methods', '__new__', '__module__',
    '__init__', '__doc__', '__call__', 'name', '__dict__', 'instance_methods',
    '_ptr', '__qualname__', '__protocols__'
]
    
class _ObjCInstance(object):
    def __init__(self, ptr, klass):
        self.name = ""
        ptr = getattr(ptr, '_objc_ptr', None) or ptr
        self._instance = ptr
        self._as_parameter_ = self._instance
        self._ptr = object_getClass(ptr)
        self._objc_method_names = get_instance_method_names(self)
        self._ivars = get_ivars(self)
        self._properties = get_properties(self)
        # print(self._properties)
        self._methods = {x.replace(":", "_"): x for x in self._objc_method_names}
        self.overrides = getattr(klass, 'overrides', {})
        self.klass = klass
        
    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in self.overrides:
                m = self.overrides[name]
                if hasattr(m, 'instance'):
                    m.instance = self.klass
                return m
                
            if name in self._ivars:
                typeptr = ivar_getTypeEncoding(self._ivars[name])
                object_getIvar.restype = decode_ivar(typeptr.decode())
                p = object_getIvar(self._instance, self._ivars[name])
                return _ObjCInstance(p, None)
                
            if name in self._properties:
                getter = self._properties[name].getter
                if getter in self._methods:
                    m = self._methods[name]
                    return _ObjCInstanceMethod(self, m)()
                
            if name in self._methods:
                m = self._methods[name]
                return _ObjCInstanceMethod(self, m)
        raise AttributeError("Cannot find attribute '{}'".format(name))
            
    def __setattr__(self, name, value):
        if '_properties' in self.__dict__:
            if name in self.__dict__: return 
            if name in self._ivars:
                typeptr = ivar_getTypeEncoding(self._ivars[name])
                object_setIvar.argtypes = [
                    c_void_p, c_void_p, decode_ivar(typeptr.decode())
                ]
                object_setIvar(self._instance, self._ivars[name], value)
                return
            if name in self._properties:
                setter = self._properties[name].setter
                if setter in self._methods:
                    m = self._methods[setter]
                    _ObjCInstanceMethod(self, m)(value)
                    return
                else:
                    raise AttributeError("The setter {} is not valid for '{}'".format(setter, name))
        super().__setattr__(name, value)
            
    
    def __dir__(self):
        d = list(super().__dir__())
        return d + list(self._methods)
    
    def __str__(self):
        objc_msgSend.argtypes = [c_void_p, c_void_p]
        objc_msgSend.restype = c_void_p
        desc = objc_msgSend(self._instance, sel_registerName("description".encode()))
        
        objc_msgSend.argtypes = [c_void_p, c_void_p]
        objc_msgSend.restype = c_char_p
        desc_str = objc_msgSend(desc, sel_registerName("cString".encode()))
        if desc_str is None: desc_str = super().__str__().encode()
        try:
            return desc_str.decode()
        except UnicodeDecodeError:
            return desc_str.decode('utf8', 'replace')
            
    def __getitem__(self, name):
        if not 'valueForKey_' in self._methods:
            raise RuntimeError(
                "{} does not conform to 'NSKeyValueCoding' protocol".format(
                    self
                )
            )
        m = self._methods['valueForKey_']
        NSString = findClass("NSString")()
        n = NSString.alloc().initWithUTF8String_(name.encode())
        v = _ObjCInstanceMethod(self, m)(n)
        return v
    
    def __setitem__(self, name, value):
        if not 'setValue_forKey_' in self._methods:
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
        self.sel = sel_registerName(sel_name.encode())
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
        
        restype, argtypes = decode_method(argtypes=self.argtypes, restype=self.restype)
        
        self._objc_msgSend.restype = restype
        self._objc_msgSend.argtypes = argtypes
        r = self._objc_msgSend(self.instance_ptr, self.sel, *args)
        if self.restype and self.restype.type.encode() == "@":
            return _ObjCInstance(r, self.klass)
        return r
    
class _ObjCClassMethod(object):
    def __init__(self, klass, sel_name):
        self.sel_name = sel_name
        self.sel = sel_registerName(sel_name.encode())
        self.class_ptr = klass._ptr
        self.klass = klass
        self.method = class_getClassMethod(self.class_ptr, self.sel)
        self._objc_msgSend = None
        
        signature = method_getTypeEncoding(self.method).decode()
        self.restype, self.argtypes = decode_method_signature(signature)
        
        
    def __call__(self, *args):
        if self._objc_msgSend is None:
            self._objc_msgSend = objc_msgSend
        
        restype, argtypes = decode_method(argtypes=self.argtypes, restype=self.restype)
        
        self._objc_msgSend.restype = restype
        self._objc_msgSend.argtypes = argtypes
        r = self._objc_msgSend(self.class_ptr, self.sel, *args)
        if self.restype and self.restype.type.encode() == "@":
            return _ObjCInstance(r, self.klass)
        return r
        
def get_ivars(klass):
    supers = [klass._ptr]
    properties = {}
    pointer = klass._ptr
    while True:
        break
        pointer = class_getSuperclass(pointer)
        if pointer is None: break
        supers.append(pointer)
    
    for pointer in supers:
        icount = c_uint(0)
        class_copyIvarList(pointer, byref(icount))
        res = POINTER(c_void_p * icount.value)
        class_copyIvarList.restype = res
        r = class_copyIvarList(pointer, None)
        if icount.value > 0:
            for prop in r.contents:
                if prop is None: continue
                n = ivar_getName(prop).decode()
                properties[n] = prop
        free.argtypes = [res]
        free(r)
    del supers
    del pointer
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
    supers = [klass._ptr]
    properties = {}
    pointer = klass._ptr
    while True:
        pointer = class_getSuperclass(pointer)
        if pointer is None: break
        supers.append(pointer)
    
    for pointer in supers:
        icount = c_uint(0)
        class_copyPropertyList(pointer, byref(icount))
        res = POINTER(c_void_p * icount.value)
        class_copyPropertyList.restype = res
        r = class_copyPropertyList(pointer, None)
        if icount.value > 0:
            for prop in r.contents:
                if prop is None: continue
                n = property_getName(prop).decode()
                properties[n] = _Property(prop, n)
        free.argtypes = [res]
        free(r)
    del supers
    del pointer
    return properties
        
def get_instance_method_names(klass):
    supers = [klass._ptr]
    methods = []
    pointer = klass._ptr
    while True:
        pointer = class_getSuperclass(pointer)
        if pointer is None: break
        supers.append(pointer)
    for pointer in supers:
        method_num = c_uint()
        class_copyMethodList(pointer, byref(method_num))
        class_copyMethodList.restype = POINTER(c_void_p * method_num.value)
        methodList = class_copyMethodList(pointer, None)
        if method_num.value < 1:
            continue
        for method in methodList.contents:
            name = method_getName(method).decode()
            if name in methods: continue
            methods.append(name)
        free.argtypes = [class_copyMethodList.restype]
        free(methodList)
    return methods
        
        
def get_class_method_names(klass):
    supers = [klass._ptr]
    methods = []
    lp = klass._ptr
    while True:
        lp = class_getSuperclass(lp)
        if lp is None: break
        supers.append(lp)
    # print(supers)
    for pointer in supers:
        meta = objc_getMetaClass(class_getName(pointer))
        if class_isMetaClass(meta):
            method_num = c_uint()
            class_copyMethodList(meta, byref(method_num))
            class_copyMethodList.restype = POINTER(c_void_p * method_num.value)
            methodList = class_copyMethodList(meta, None)
            if method_num.value < 1:
                continue
            for method in methodList.contents:
                name = method_getName(method).decode()
                if name in methods: continue
                methods.append(name)
            free.argtypes = [class_copyMethodList.restype]
            free(methodList)
        else:
            raise RuntimeError("Could not find the MetaClass for '{}'".format(
                class_getName(pointer)
            ))
    return methods

class _ObjCClass(object):
    def __init__(self, wrapper):
        self.name = wrapper.name
        self._ptr = wrapper._ptr
        self._protocols = wrapper.__protocols__
        # print("Class PTR", self._ptr)
        
        self.overrides = getattr(wrapper, 'overrides', {})
        
        self._objc_method_names = get_class_method_names(self)
        self._methods = {x.replace(":", "_"): x for x in self._objc_method_names}
        
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
            klass = super(_ObjCClassType, metaclass).__new__(metaclass, name, bases, namespace)
            
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
                if k in methodIgnores: continue
                if getattr(v, '_property', False):
                    status = class_addIvar(
                        new_klass,
                        k.encode(),
                        v.sizep,
                        v.alignp,
                        v._typeEncoding.encode()
                    )
                    
                    names.append(k)
                    continue
                
                if not getattr(v, '_instanceMethod', False): continue
                if any([getattr(p, k, False) for p in klass.__protocols__]):
                    c = False
                    for p in [getattr(p, k, None) for p in klass.__protocols__]:
                        if p is None: continue
                        c = p._instanceMethod
                    if not c: continue
                if getattr(v, '_objc_super', None) is not None:
                    class_addMethod.argtypes = [c_void_p, c_void_p, v._cFuncType, c_char_p]
                    class_addMethod(
                        new_klass,
                        sel_registerName(v._funcname.encode()),
                        v._cFunc,
                        (v._restype + "".join(v._argtypes)).encode()
                    )
                    names.append(k)
                    continue
                    
            objc_registerClassPair(new_klass)
            
            meta_klass = objc_getMetaClass(class_getName(new_klass))
            
            for k, v in namespace.items():
                if k in methodIgnores: continue
                if getattr(v, '_instanceMethod', True): continue
                if any([getattr(p, k, False) for p in klass.__protocols__]):
                    c = False
                    for p in [getattr(p, k, None) for p in klass.__protocols__]:
                        if p is None: continue
                        c = p._instanceMethod
                    if c: continue
                if getattr(v, '_objc_super', None) is not None:
                    print("Adding Classmethod {}".format(k))
                    class_addMethod.argtypes = [c_void_p, c_void_p, v._cFuncType, c_char_p]
                    class_addMethod(
                        meta_klass,
                        sel_registerName(v._funcname.encode()),
                        v._cFunc,
                        (v._restype + "".join(v._argtypes)).encode()
                    )
                    names.append(k)
            
            # print("New Class PTR", new_klass)
            klass._ptr = new_klass
            
            klass.overrides = {}
            
            class WrappedOverride(object):
                instance = None
                
                def __init__(self, function):
                    self.func = function
                    
                def __call__(self, *args, **kwargs):
                    self.func(self.instance, *args, **kwargs)
            
            for n in namespace:
                if n in methodIgnores: continue
                if n in names: continue
                # print(n)
                if callable(namespace[n]):
                    # print("wrapping function")
                    # Function
                    func = WrappedOverride(namespace[n])
                else:
                    # Property / Variable
                    func = namespace[n]
                # dict(klass.__dict__)[n] = func
                klass.overrides[n] = func
            
            return klass
        elif len(args) == 3:
            self, name, ptr = args
            klass = super(_ObjCClassType, self).__new__(self, name, (object,), dict(self.__dict__))
            d = dict(self.__dict__)
            klass.name = name
            klass._ptr = ptr
            return klass
            
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
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
            klass = super(_ObjCProtocolType, metaclass).__new__(metaclass, name, bases, namespace)
            i = 0
            basename = name
            while True:
                if objc_getProtocol(name.encode()) is not None:
                    i += 1
                    name = "{}_{}".format(basename, i)
                else:
                    break
            # print("Creating New ObjC Object")
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
                if k in methodIgnores: continue
                if getattr(v, '_objc_super', None) is not None:
                    # class_addMethod.argtypes = [c_void_p, c_void_p, v._cFuncType, c_char_p]
                    protocol_addMethodDescription(
                        new_klass,
                        sel_registerName(v._funcname.encode()),
                        (v._restype + "".join(v._argtypes)).encode(),
                        v._requiredMethod,
                        v._instanceMethod,
                    )
                    
                    print(protocol_getMethodDescription(
                        new_klass,
                        sel_registerName(v._funcname.encode()),
                        v._requiredMethod,
                        v._instanceMethod
                    ))
                    
            objc_registerProtocol(new_klass)
            
            # print("New Class PTR", new_klass)
            klass._ptr = new_klass
            
            return klass
        elif len(args) == 3:
            self, name, ptr = args
            klass = super(_ObjCProtocolType, self).__new__(self, name, (object,), dict(self.__dict__))
            d = dict(self.__dict__)
            klass.name = name
            klass._ptr = ptr
            return klass
            
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        return _ObjCProtocol(self)
    
        
def objc_super(_self, _command, argtypes=None, restype=None, *args):
    signature = restype + "".join(argtypes)
    restype, argtypes = decode_method_signature(signature)
    restype, argtypes = decode_method(argtypes=argtypes, restype=restype)
    
    objc_msgSendSuper.argtypes = argtypes
    objc_msgSendSuper.restype = restype
    print(objc_msgSendSuper.argtypes, objc_msgSendSuper.restype)
    print(object_getClass(_self))
    print(_self, _command, args)
    return objc_msgSendSuper(object_getClass(_self), _command, *args)
    
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
                # print(function.__annotations__)
                self._restype = function.__annotations__['return'] if 'return' in function.__annotations__ else 'v'
                # print(self._restype)
            if self._argtypes is None:
                a = ['@', ':']
                for k,v in function.__annotations__.items():
                    if k == 'return': continue
                    a.append(v if v else '?')
                self._argtypes = a
            if self._cFunc is None:
                self._signature = self._restype + "".join(self._argtypes)
                restype, argtypes = decode_method_signature(self._signature)
                restype, argtypes = decode_method(argtypes=argtypes, restype=restype)
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
                
        
def objc_method(funcname=None, argtypes=None, restype=None, instanceMethod=True):
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
                # print(function.__annotations__)
                self._restype = function.__annotations__['return'] if 'return' in function.__annotations__ else 'v'
                # print(self._restype)
            if self._argtypes is None:
                a = ['@', ':']
                for k,v in function.__annotations__.items():
                    if k == 'return': continue
                    a.append(v if v else '?')
                self._argtypes = a
            self._signature = self._restype + "".join(self._argtypes)
            restype, argtypes = decode_method_signature(self._signature)
            restype, argtypes = decode_method(argtypes=argtypes, restype=restype)
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
            t, self.sizep, self.alignp = NSGetSizeAndAlignment(self._typeEncoding)
            
    return _Property()
    
def objc_privateProperty(initialValue):
    pass

def _getClassList():
    r = objc_getClassList(None, 0)
    t = (c_void_p * r)
    objc_getClassList.argtypes = [POINTER(t), c_int]
    a = t()
    objc_getClassList(byref(a), r)
    n = {}
    for i in list(a):
        cn = class_getName(i).decode()
        if cn.startswith("_"): continue
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
        else:
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
    
    
# Install the loaders for obj.classes and objc.protocols (can only be used once Class and Protocol has been defined, respectively).

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

class _ObjcSpecialFinderLoader(object):
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
        mod = sys.modules.setdefault(fullname, _MODULE_PROXIES[fullname](fullname))
        mod.__file__ = "<dynamically created by {cls.__module__}.{cls.__name__}>".format(cls=type(self))
        mod.__loader__ = self
        mod.__package__ = "objc"
        mod.__all__ = ["DontEvenTryToStarImportThisModuleYouCrazyPerson"]
        return mod

# Remove old versions of the loader and modules if the objc module is reloaded.

sys.meta_path.append(_ObjcSpecialFinderLoader())
sys.modules.pop("objc.classes", None)
sys.modules.pop("classes", None)
sys.modules.pop("objc.protocols", None)
sys.modules.pop("protocols", None)

try:
    import classes
except (SystemError, ImportError):
    from . import classes
try:
    import protocols
except (SystemError, ImportError):
    from . import protocols

def main():
#    class JSA(findProtocol('JSExport')):
#        @objc_protocol_method(required=True)
#        def helloWorld(_self, _command) -> 'v':
#            pass
    
    class Test(findClass('NSObject')):
#        __protocols__ = [JSA]
        
        @objc_method()
        def helloWorld(_self, _command) -> 'v':
            print("Hello World")
    
    Test = Test()
    t = Test.alloc().init()
    # print(t['description'])
    # t.helloWorld()
    # print(t.description)
    
if __name__ == '__main__':
    main()

__all__ = [
    'c', 'findClass', '_ObjCInstance', 'cacheAllClasses',
    'objc_method','objc_super', 'sel_registerName', 'class_getName',
    'object_getClass', 'object_getClassName', 'findProtocol',
    'objc_protocol_method', 'protocol_conformsToProtocol',
    'objc_instanceProperty', '_MODULE_PROXIES', 'objc_privateProperty'
]

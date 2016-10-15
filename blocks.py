from ctypes import (
    CFUNCTYPE, Structure, c_void_p, c_int, POINTER, byref, pointer,
    sizeof, c_ulong, c_char_p
)

try:
    from objc_encoding import (
        decode_method, decode_method_signature
    )
except ImportError as e:
    from .objc_encoding import (
        decode_method, decode_method_signature
    )
    
try:
    from _functions import objc_getClass
except ImportError:
    from ._functions import objc_getClass
    
BLOCK_HAS_COPY_DISPOSE =  (1 << 25)
BLOCK_HAS_CTOR =          (1 << 26) # helpers have C++ code
BLOCK_IS_GLOBAL =         (1 << 28)
BLOCK_HAS_STRET =         (1 << 29) # IFF BLOCK_HAS_SIGNATURE
BLOCK_HAS_SIGNATURE =     (1 << 30)

_cached_blocks = {}


class Block_descriptor_1(Structure):
    _fields_ = [
        ('reserved', c_ulong),
        ('size', c_ulong),
        ('signature', c_char_p),
        # ('copy_helper', c_void_p),
        # ('dispose_helper', c_void_p),
    ]


class _ObjCBlock(object):
    def __new__(cls, func):
        if func in _cached_blocks:
            return _cached_blocks[func]
        self = super(cls, _ObjCBlock).__new__(cls)
        self.func = func
        _cached_blocks[func] = self
        return self
        
    def __init__(self, func):
        argtypes = func.__annotations__
        sigit = []
        if 'return' in argtypes:
            sigit.append(argtypes.pop('return'))
        else:
            sigit.append('v')
        sigit.extend(argtypes.values())
        signature = ''.join(sigit)
        restype, argtypes = decode_method_signature(signature)
        restype, argtypes = decode_method(argtypes=argtypes, restype=restype)
        InvokeFuncType = CFUNCTYPE(restype, *argtypes)
        self.invoke_method = InvokeFuncType(func)
        class Block_literal_1(Structure):
            _fields_ = [
                ('isa', c_void_p),
                ('flags', c_int),
                ('reserved', c_int),
                ('invoke', InvokeFuncType),
                ('descriptor', POINTER(Block_descriptor_1)),
            ]
        self._ctype = Block_literal_1
        block = Block_literal_1()
        klass = objc_getClass('__NSGlobalBlock'.encode())
        block.isa = klass
        # print(BLOCK_IS_GLOBAL | BLOCK_HAS_STRET)
        block.flags = 0x50000000 # BLOCK_IS_GLOBAL | BLOCK_HAS_STRET
        print(block.flags)
        block.reserved = 0
        block.invoke = self.invoke_method
        descriptor = Block_descriptor_1()
        descriptor.reserved = 0
        descriptor.size = sizeof(Block_literal_1)
        # descriptor.copy_helper = None
        # descriptor.dispose_helper = None
        descriptor.signature = signature.encode()
        block.descriptor = pointer(descriptor)
        self.block = block
        self._as_paramater_ = block
        
    def __call__(self, *args):
        return self.invoke_method(*args)
        
def main():
    def blockFunc(arg0: 'B', arg1: '@') -> 'v':
        print(arg0, arg1)
    
    block = _ObjCBlock(blockFunc)
    block(True, 10)
    
if __name__ == '__main__':
    main()

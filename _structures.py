from ctypes import *


class objc_method_description(Structure):
    _fields_ = [
        ('name', c_void_p),
        ('types', c_char_p),
    ]
    
    def __str__(self):
        return "<name: {}, types: {}>".format(self.name, self.types)


class objc_super(Structure):
    _fields_ = [
        ('reciever', c_void_p),
        ('class', c_void_p)
    ]
    

class objc_ivar(Structure):
    _fields_ = [
        ('ivar_name', c_char_p),
        ('ivar_type', c_char_p),
        ('ivar_offset', c_int),
        ('space', c_int)
    ]
    
    def __str__(self):
        return "<objc_ivar object at 0x{} {} {} {} {}>".format(
            id(self),
            self.ivar_name.decode(),
            self.ivar_type.decode() if self.ivar_type else '',
            self.ivar_offset,
            self.space
        )


class objc_property_attribute_t(Structure):
    _fields_ = [
        ('name', c_char_p),
        ('value', c_char_p)
    ]

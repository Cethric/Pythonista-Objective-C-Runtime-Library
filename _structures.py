from ctypes import (
    Structure, c_void_p, c_char_p, c_int, c_ulong
)


class objc_method_description(Structure):
    _fields_ = [
        ('name', c_void_p),
        ('types', c_char_p),
    ]

    def __str__(self):
        return "<name: {}, types: {}>".format(self.name, self.types)


class objc_super_struct(Structure):
    _fields_ = [
        ('receiver', c_void_p),
        ('class', c_void_p)
    ]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __str__(self):
        return "<objc_super object at 0x{}. Reciever: {} Class: {}>".format(
            id(self),
            self.reciever,
            self['class']
        )


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


def main():
    block = Block_literal_1()
    block.isa = None
    block.flags = 0
    block.reserved = 0
    block.invoke = None
    descriptor = Block_descriptor_1()
    descriptor.reserver = None
    descriptor.size = 0
    descriptor.copy_helper = None
    descriptor.dispose_helper = None
    descriptor.signature = None
    block.descriptor = descriptor
    
    print(block)

if __name__ == '__main__':
    main()

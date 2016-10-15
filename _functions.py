from ctypes import (
    cdll, CDLL, POINTER, byref,
    c_bool, c_size_t,
    c_void_p,
    c_char_p,
    c_int, c_uint, c_uint8
)

try:
    from _structures import (
        objc_property_attribute_t, objc_method_description
    )
except ImportError:
    from ._structures import (
        objc_property_attribute_t, objc_method_description
    )


try:
    c = cdll.LoadLibrary("Foundation.framework/Foundation")
    c = cdll.LoadLibrary("Cocoa.framework/Cocoa")
except OSError:
    # print("Can not Dynamically load Foundation.framework or Cocoa.framework")
    pass
c = CDLL(None)

free = c.free
free.argtypes = [c_void_p]
free.restype = None

class_getName = c.class_getName
class_getName.argtypes = [c_void_p]
class_getName.restype = c_char_p

class_getSuperclass = c.class_getSuperclass
class_getSuperclass.argtypes = [c_void_p]
class_getSuperclass.restype = c_void_p

class_setSuperclass = c.class_setSuperclass
class_setSuperclass.argtypes = [c_void_p, c_void_p]
class_setSuperclass.restype = c_void_p

class_isMetaClass = c.class_isMetaClass
class_isMetaClass.argtypes = [c_void_p]
class_isMetaClass.restype = c_bool

class_getInstanceSize = c.class_getInstanceSize
class_getInstanceSize.argtypes = [c_void_p]
class_getInstanceSize.restype = c_size_t

class_getInstanceVariable = c.class_getInstanceVariable
class_getInstanceVariable.argtypes = [c_void_p, c_char_p]
class_getInstanceVariable.restype = c_void_p

class_getClassVariable = c.class_getClassVariable
class_getClassVariable.argtypes = [c_void_p, c_char_p]
class_getClassVariable.restype = c_void_p

class_addIvar = c.class_addIvar
class_addIvar.argtypes = [c_void_p, c_char_p, c_size_t, c_uint8, c_char_p]
class_addIvar.restype = c_bool

class_copyIvarList = c.class_copyIvarList
class_copyIvarList.argtypes = [c_void_p, POINTER(c_uint)]
class_copyIvarList.restype = POINTER(c_void_p)

class_getIvarLayout = c.class_getIvarLayout
class_getIvarLayout.argtypes = [c_void_p]
class_getIvarLayout.restype = c_char_p

class_setIvarLayout = c.class_setIvarLayout
class_setIvarLayout.argtypes = [c_void_p, c_char_p]
class_setIvarLayout.restype = None

class_getWeakIvarLayout = c.class_getWeakIvarLayout
class_getWeakIvarLayout.argtypes = [c_void_p]
class_getWeakIvarLayout.restype = c_char_p

class_setWeakIvarLayout = c.class_setWeakIvarLayout
class_setWeakIvarLayout.argtypes = [c_void_p, c_char_p]
class_setWeakIvarLayout.restype = None

class_getProperty = c.class_getProperty
class_getProperty.argtypes = [c_void_p, c_char_p]
class_getProperty.restype = c_void_p

class_copyPropertyList = c.class_copyPropertyList
class_copyPropertyList.argtypes = [c_void_p, POINTER(c_uint)]
class_copyPropertyList.restype = POINTER(c_void_p)

class_addMethod = c.class_addMethod
class_addMethod.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p]
class_addMethod.restype = c_bool

class_getInstanceMethod = c.class_getInstanceMethod
class_getInstanceMethod.argtypes = [c_void_p, c_void_p]
class_getInstanceMethod.restype = c_void_p

class_getClassMethod = c.class_getClassMethod
class_getClassMethod.argtypes = [c_void_p, c_void_p]
class_getClassMethod.restype = c_void_p

class_copyMethodList = c.class_copyMethodList
class_copyMethodList.argtypes = [c_void_p, POINTER(c_uint)]
class_copyMethodList.restype = c_void_p

class_replaceMethod = c.class_replaceMethod
class_replaceMethod.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p]
class_replaceMethod.restype = c_void_p

class_getMethodImplementation = c.class_getMethodImplementation
class_getMethodImplementation.argtypes = [c_void_p, c_void_p]
class_getMethodImplementation.restype = c_void_p

class_respondsToSelector = c.class_respondsToSelector
class_respondsToSelector.argtypes = [c_void_p, c_void_p]
class_respondsToSelector.restype = c_bool

class_addProtocol = c.class_addProtocol
class_addProtocol.argtypes = [c_void_p, c_void_p]
class_addProtocol.restype = c_bool

class_addProperty = c.class_addProperty
class_addProperty.argtypes = [
    c_void_p, c_char_p, objc_property_attribute_t, c_uint
]
class_addProperty.restype = c_bool

class_replaceProperty = c.class_replaceProperty
class_replaceProperty.argtypes = [c_void_p, c_char_p, c_void_p, c_uint]
class_replaceProperty.restype = None

class_conformsToProtocol = c.class_conformsToProtocol
class_conformsToProtocol.argtypes = [c_void_p, c_void_p]
class_conformsToProtocol.restype = c_bool

class_copyProtocolList = c.class_copyProtocolList
class_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]
class_copyProtocolList.restype = c_void_p

class_getVersion = c.class_getVersion
class_getVersion.argtypes = [c_void_p]
class_getVersion.restype = c_int

class_setVersion = c.class_setVersion
class_setVersion.argtypes = [c_void_p, c_int]
class_setVersion.restype = None

objc_allocateClassPair = c.objc_allocateClassPair
objc_allocateClassPair.argtypes = [c_void_p, c_char_p, c_size_t]
objc_allocateClassPair.restype = c_void_p

objc_disposeClassPair = c.objc_disposeClassPair
objc_disposeClassPair.argtypes = [c_void_p]
objc_disposeClassPair.restype = None

objc_registerClassPair = c.objc_registerClassPair
objc_registerClassPair.argtypes = [c_void_p]
objc_registerClassPair.restype = None

class_createInstance = c.class_createInstance
class_createInstance.argtypes = [c_void_p, c_size_t]
class_createInstance.restype = c_void_p

objc_constructInstance = c.objc_constructInstance
objc_constructInstance.argtypes = [c_void_p, POINTER(c_void_p)]
objc_constructInstance.restype = c_void_p

objc_destructInstance = c.objc_destructInstance
objc_destructInstance.argtypes = [c_void_p]
objc_destructInstance.restype = None

object_copy = c.object_copy
object_copy.argtypes = [c_void_p, c_size_t]
object_copy.restype = c_void_p

object_dispose = c.object_dispose
object_dispose.argtypes = [c_void_p]
object_dispose.restype = None

object_setInstanceVariable = c.object_setInstanceVariable
object_setInstanceVariable.argtypes = [c_void_p, c_char_p, POINTER(c_void_p)]
object_setInstanceVariable.restype = c_void_p

object_getInstanceVariable = c.object_getInstanceVariable
object_getInstanceVariable.argtypes = [c_void_p, c_char_p, POINTER(c_void_p)]
object_getInstanceVariable.restype = c_void_p

object_getIndexedIvars = c.object_getIndexedIvars
object_getIndexedIvars.argtypes = [c_void_p]
object_getIndexedIvars.restype = None

object_getIvar = c.object_getIvar
object_getIvar.argtypes = [c_void_p, c_void_p]
object_getIvar.restype = c_void_p

object_setIvar = c.object_setIvar
object_setIvar.argtypes = [c_void_p, c_void_p, c_void_p]
object_setIvar.restype = None

object_getClassName = c.object_getClassName
object_getClassName.argtypes = [c_void_p]
object_getClassName.restype = c_char_p

object_getClass = c.object_getClass
object_getClass.argtypes = [c_void_p]
object_getClass.restype = c_void_p

object_setClass = c.object_setClass
object_setClass.argtypes = [c_void_p, c_void_p]
object_setClass.restype = c_void_p

objc_getClassList = c.objc_getClassList
objc_getClassList.argtypes = [POINTER(c_void_p), c_int]
objc_getClassList.restype = c_int

objc_copyClassList = c.objc_copyClassList
objc_copyClassList.argtypes = [POINTER(c_uint)]
objc_copyClassList.restype = c_void_p

objc_lookUpClass = c.objc_lookUpClass
objc_lookUpClass.argtypes = [c_char_p]
objc_lookUpClass.restype = c_void_p

objc_getClass = c.objc_getClass
objc_getClass.argtypes = [c_char_p]
objc_getClass.restype = c_void_p

objc_getRequiredClass = c.objc_getRequiredClass
objc_getRequiredClass.argtypes = [c_char_p]
objc_getRequiredClass.restype = c_void_p

objc_getMetaClass = c.objc_getMetaClass
objc_getMetaClass.argtypes = [c_char_p]
objc_getMetaClass.restype = c_void_p

ivar_getName = c.ivar_getName
ivar_getName.argtypes = [c_void_p]
ivar_getName.restype = c_char_p

ivar_getTypeEncoding = c.ivar_getTypeEncoding
ivar_getTypeEncoding.argtypes = [c_void_p]
ivar_getTypeEncoding.restype = c_char_p

ivar_getOffset = c.ivar_getOffset
ivar_getOffset.argtypes = [c_void_p]
ivar_getOffset.restype = c_void_p

objc_setAssociatedObject = c.objc_setAssociatedObject
objc_setAssociatedObject.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
objc_setAssociatedObject.restype = None

objc_getAssociatedObject = c.objc_getAssociatedObject
objc_getAssociatedObject.argtypes = [c_void_p, c_void_p]
objc_getAssociatedObject.restype = c_void_p

objc_removeAssociatedObjects = c.objc_removeAssociatedObjects
objc_removeAssociatedObjects.argtypes = [c_void_p]
objc_removeAssociatedObjects.restype = None

# objc_msgSend stub
objc_msgSend = c.objc_msgSend
objc_msgSend.restype = c_void_p

# objc_msgSendSuper stub
objc_msgSendSuper = c.objc_msgSendSuper
objc_msgSendSuper.restype = c_void_p

# method_invoke stub
method_invoke = c.method_invoke
method_invoke.restype = c_void_p
method_invoke.argtypes = [c_void_p, c_void_p]

method_getName = c.method_getName
method_getName.argtypes = [c_void_p]
method_getName.restype = c_char_p

method_getImplementation = c.method_getImplementation
method_getImplementation.argtypes = [c_void_p]
method_getImplementation.restype = c_void_p

method_getTypeEncoding = c.method_getTypeEncoding
method_getTypeEncoding.argtypes = [c_void_p]
method_getTypeEncoding.restype = c_char_p

method_copyReturnType = c.method_copyReturnType
method_copyReturnType.argtypes = [c_void_p]
method_copyReturnType.restype = c_char_p

method_copyArgumentType = c.method_copyArgumentType
method_copyArgumentType.argtypes = [c_void_p, c_uint]
method_copyArgumentType.restype = c_char_p

method_getReturnType = c.method_getReturnType
method_getReturnType.argtypes = [c_void_p, POINTER(c_char_p), c_size_t]
method_getReturnType.restype = None

method_getNumberOfArguments = c.method_getNumberOfArguments
method_getNumberOfArguments.argtypes = [c_void_p]
method_getNumberOfArguments.restype = c_uint

method_getArgumentType = c.method_getArgumentType
method_getArgumentType.argtypes = [
    c_void_p, c_uint, POINTER(c_char_p), c_size_t
]
method_getArgumentType.restype = None

method_getDescription = c.method_getDescription
method_getDescription.argtypes = [c_void_p]
method_getDescription.restype = c_void_p

method_setImplementation = c.method_setImplementation
method_setImplementation.argtypes = [c_void_p, c_void_p]
method_setImplementation.restype = c_void_p

method_exchangeImplementations = c.method_exchangeImplementations
method_exchangeImplementations.argtypes = [c_void_p, c_void_p]
method_exchangeImplementations.restype = None

objc_copyImageNames = c.objc_copyImageNames
objc_copyImageNames.argtypes = [POINTER(c_uint)]
objc_copyImageNames.restype = c_char_p

class_getImageName = c.class_getImageName
class_getImageName.argtypes = [c_void_p]
class_getImageName.restype = c_char_p

objc_copyClassNamesForImage = c.objc_copyClassNamesForImage
objc_copyClassNamesForImage.argtypes = [POINTER(c_char_p), c_uint]
objc_copyClassNamesForImage.restype = c_char_p

sel_getName = c.sel_getName
sel_getName.argtypes = [c_void_p]
sel_getName.restype = c_char_p

sel_registerName = c.sel_registerName
sel_registerName.argtypes = [c_char_p]
sel_registerName.restype = c_void_p

sel_getUid = c.sel_getUid
sel_getUid.argtypes = [c_char_p]
sel_getUid.restype = c_void_p

sel_isEqual = c.sel_isEqual
sel_isEqual.argtypes = [c_void_p, c_void_p]
sel_isEqual.restype = c_bool

objc_getProtocol = c.objc_getProtocol
objc_getProtocol.argtypes = [c_char_p]
objc_getProtocol.restype = c_void_p

objc_copyProtocolList = c.objc_copyProtocolList
objc_copyProtocolList.argtypes = [POINTER(c_uint)]
objc_copyProtocolList.restype = c_void_p

objc_allocateProtocol = c.objc_allocateProtocol
objc_allocateProtocol.argtypes = [c_char_p]
objc_allocateProtocol.restype = c_void_p

objc_registerProtocol = c.objc_registerProtocol
objc_registerProtocol.argtypes = [c_void_p]
objc_registerProtocol.restype = None

protocol_addMethodDescription = c.protocol_addMethodDescription
protocol_addMethodDescription.argtypes = [
    c_void_p, c_void_p, c_char_p, c_bool, c_bool
]
protocol_addMethodDescription.restype = None

protocol_addProtocol = c.protocol_addProtocol
protocol_addProtocol.argtypes = [c_void_p, c_void_p]
protocol_addProtocol.restype = None

protocol_addProperty = c.protocol_addProperty
protocol_addProperty.argtypes = [
    c_void_p, c_char_p, c_void_p, c_uint, c_bool, c_bool
]
protocol_addProperty.restype = None

protocol_getName = c.protocol_getName
protocol_getName.argtypes = [c_void_p]
protocol_getName.restype = c_char_p

protocol_isEqual = c.protocol_isEqual
protocol_isEqual.argtypes = [c_void_p, c_void_p]
protocol_isEqual.restype = c_bool

protocol_copyMethodDescriptionList = c.protocol_copyMethodDescriptionList
protocol_copyMethodDescriptionList.argtypes = [
    c_void_p, c_bool, c_bool, c_uint
]
protocol_copyMethodDescriptionList.restype = c_void_p

protocol_getMethodDescription = c.protocol_getMethodDescription
protocol_getMethodDescription.argtypes = [c_void_p, c_void_p, c_bool, c_bool]
protocol_getMethodDescription.restype = objc_method_description

protocol_copyPropertyList = c.protocol_copyPropertyList
protocol_copyPropertyList.argtypes = [c_void_p, c_uint]
protocol_copyPropertyList.restype = c_void_p

protocol_getProperty = c.protocol_getProperty
protocol_getProperty.argtypes = [c_void_p, c_char_p, c_bool, c_bool]
protocol_getProperty.restype = c_void_p

protocol_copyProtocolList = c.protocol_copyProtocolList
protocol_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]
protocol_copyProtocolList.restype = c_void_p

protocol_conformsToProtocol = c.protocol_conformsToProtocol
protocol_conformsToProtocol.argtypes = [c_void_p, c_void_p]
protocol_conformsToProtocol.restype = c_bool

property_getName = c.property_getName
property_getName.argtypes = [c_void_p]
property_getName.restype = c_char_p

property_getAttributes = c.property_getAttributes
property_getAttributes.argtypes = [c_void_p]
property_getAttributes.restype = c_char_p

property_copyAttributeValue = c.property_copyAttributeValue
property_copyAttributeValue.argtypes = [c_void_p, c_char_p]
property_copyAttributeValue.restype = c_char_p

property_copyAttributeList = c.property_copyAttributeList
property_copyAttributeList.argtypes = [c_void_p, POINTER(c_uint)]
property_copyAttributeList.restype = c_void_p

objc_enumerationMutation = c.objc_enumerationMutation
objc_enumerationMutation.argtypes = [c_void_p]
objc_enumerationMutation.restype = None

objc_setEnumerationMutationHandler = c.objc_setEnumerationMutationHandler
objc_setEnumerationMutationHandler.argtypes = [c_void_p]
objc_setEnumerationMutationHandler.restype = None

imp_implementationWithBlock = c.imp_implementationWithBlock
imp_implementationWithBlock.argtypes = [c_void_p]
imp_implementationWithBlock.restype = c_void_p

imp_getBlock = c.imp_getBlock
imp_getBlock.argtypes = [c_void_p]
imp_getBlock.restype = c_void_p

imp_removeBlock = c.imp_removeBlock
imp_removeBlock.argtypes = [c_void_p]
imp_removeBlock.restype = c_bool

objc_loadWeak = c.objc_loadWeak
objc_loadWeak.argtypes = [c_void_p]
objc_loadWeak.restype = c_void_p

objc_storeWeak = c.objc_storeWeak
objc_storeWeak.argtypes = [c_void_p, POINTER(c_void_p)]
objc_storeWeak.restype = c_void_p


UIApplicationMain = c.UIApplicationMain
UIApplicationMain.argtypes = [c_int, (c_char_p * 0), c_void_p, c_void_p]
UIApplicationMain.restype = c_int

NSStringFromClass = c.NSStringFromClass
NSStringFromClass.argtypes = [c_void_p]
NSStringFromClass.restype = c_void_p


def NSGetSizeAndAlignment(typeptr):
    func = c.NSGetSizeAndAlignment
    func.argtypes = [c_char_p, POINTER(c_uint), POINTER(c_uint)]
    func.restype = c_char_p
    sizep = c_uint(0)
    alignp = c_uint(0)
    t = func(typeptr.encode(), byref(sizep), byref(alignp))
    return t, sizep.value, alignp.value

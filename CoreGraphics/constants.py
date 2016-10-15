from ctypes import c_int32

CGError = c_int32


kCGErrorSuccess = 0
kCGErrorFailure = 1000
kCGErrorIllegalArgument = 1001
kCGErrorInvalidConnection = 1002
kCGErrorInvalidContext = 1003
kCGErrorCannotComplete = 1004
kCGErrorNameTooLong = 1005
kCGErrorNotImplemented = 1006
kCGErrorRangeCheck = 1007
kCGErrorTypeCheck = 1008
kCGErrorNoCurrentPoint = 1009
kCGErrorInvalidOperation = 1010
kCGErrorNoneAvailable = 1011
kCGErrorApplicationRequiresNewerSystem = 1015
kCGErrorApplicationNotPermittedToExecute = 1016
kCGErrorApplicationIncorrectExecutableFormatFound = 1023
kCGErrorApplicationIsLaunching = 1024
kCGErrorApplicationAlreadyRunning = 1025
kCGErrorApplicationCanOnlyBeRunInOneSessionAtATime = 1026
kCGErrorClassicApplicationsMustBeLaunchedByClassic = 1027
kCGErrorForkFailed = 1028
kCGErrorRetryRegistration = 1029

__all__ = [
    'CGError', 'kCGErrorSuccess', 'kCGErrorFailure', 'kCGErrorIllegalArgument',
    'kCGErrorInvalidConnection', 'kCGErrorInvalidContext',
    'kCGErrorCannotComplete', 'kCGErrorNameTooLong', 'kCGErrorNotImplemented',
    'kCGErrorRangeCheck', 'kCGErrorTypeCheck', 'kCGErrorNoCurrentPoint',
    'kCGErrorInvalidOperation', 'kCGErrorNoneAvailable',
    'kCGErrorApplicationRequiresNewerSystem',
    'kCGErrorApplicationNotPermittedToExecute',
    'kCGErrorApplicationIncorrectExecutableFormatFound',
    'kCGErrorApplicationIsLaunching', 'kCGErrorApplicationAlreadyRunning',
    'kCGErrorApplicationCanOnlyBeRunInOneSessionAtATime',
    'kCGErrorClassicApplicationsMustBeLaunchedByClassic', 'kCGErrorForkFailed',
    'kCGErrorRetryRegistration'
]

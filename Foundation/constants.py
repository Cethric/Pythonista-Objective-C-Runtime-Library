class NSEnumerationOptions():
    NSEnumerationConcurrent = 1 << 0
    NSEnumerationReverse = 1 << 1


class NSComparisonResult():
    NSOrderedAscending = -1
    NSOrderedSame = 0
    NSOrderedDescending = 1


class NSSortOptions():
    NSSortConcurrent = 1 << 0
    NSSortStable = 1 << 4


class NSQualityofService():
    NSQualityofServiceUserInteractive = 0x21
    NSQualityofServiceUserInitiated = 0x19
    NSQualityofServiceUtility = 0x11
    NSQualityofServiceBackground = 0x09
    NSQualityofServiceDefault = -1


class NSSearchPathDirectory():
    ApplicationDirectory = 1
    DemoApplicationDirectory = 2
    DeveloperApplicationDirectory = 3
    AdminApplicationDirectory = 4
    LibraryDirectory = 5
    DeveloperDirectory = 6
    UserDirectory = 7
    DocumentationDirectory = 8
    DocumentDirectory = 9
    CoreServiceDirectory = 10
    AutosavedInformationDirectory = 11
    DesktopDirectory = 12
    CachesDirectory = 13
    ApplicationSupportDirectory = 14
    DownloadsDirectory = 15
    InputMethodsDirectory = 16
    MoviesDirectory = 17
    MusicDirectory = 18
    PicturesDirectory = 19
    PrinterDescriptionDirectory = 20
    SharedPublicDirectory = 21
    PreferencePanesDirectory = 22
    ItemReplacementDirectory = 99
    AllApplicationsDirectory = 100
    AllLibrariesDirectory = 101


class NSSearchPathDomainMask():
    UserDomainMask = 1
    LocalDomainMask = 2
    SystemDomainMask = 4
    AllDomainsMask = 0x0ffff


class NSErrorCodes():
    NoSuchFileError = 4
    LockingError = 255
    ReadUnknownError = 256
    ReadNoPermissionError = 257
    ReadInvalidFileNameError = 258
    ReadCorruptFileError = 259
    ReadNoSuchFileError = 260
    ReadInapplicableStringEncodingError = 261
    ReadUnsuppoertedSchemeError = 262
    ReadTooLargeError = 263
    ReadUnknownStringEncodingError = 264

    WriteUnknownError = 512
    WriteNoPermissionsError = 513
    WriteInvalidFileNameError = 514
    WriteFileExistsError = 515
    WriteInapplicableStringEncodingError = 516
    WriteUnsupportedSchemeError = 517
    WriteOutOfSpaceError = 540
    WriteVolumeReadOnlyError = 642

    KeyValueValidationError = 1024
    FormattingError = 2048
    UserCancelledError = 3072
    FeatureUnsupportedError = 3328

    FileErrorMinimum = 0
    FileErrorMaximum = 1023
    ValidationErrorMinimum = 1024
    ValidationErrorMaximum = 2047
    FormattingErrorMinimum = 2048
    FormattingErrorMaximum = 2559

    PropertyListReadCorruptError = 3840
    PropertyListUnknownVersionError = 3841
    PropertyListReadStreamError = 3842
    PropertyListWriteStreamError = 3843
    PropertyListErrorMinimum = 3840
    PropertyListErrorMaximum = 4095

    ExecutableErrorMinumum = 3584
    ExecutableNotLoadableError = 3584
    ExecutableArchitectureMismatchError = 3585
    ExecutableRuntimeMismatchError = 3586
    ExecutableLoadError = 3587
    ExecutableLinkError = 3588
    ExecutableErrorMaximum = 3839

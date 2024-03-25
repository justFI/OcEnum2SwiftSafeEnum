# OcEnum2SwiftSafeEnum
Base the oc file of protobuf generate  

Extension Oc .h file GPB_ENUM code To Swift Safe Enum

example：

gender.h
```
typedef GPB_ENUM(GenderType) {
    GenderType_GPBUnrecognizedEnumeratorValue = kGPBUnrecognizedEnumeratorValue,
    GenderType_Male = 0,
    GenderType_Female = 1,
};
```
to 

gender_extension.swift
```
extension GenderType {
    public init?(rawValue: Int32) {
        switch rawValue {
        case 0: self = .male
        case 1: self = .feMale
        default:
            self = .male
            print("catch enum:GenderType error case:\(rawValue), restore to defalut \(GenderType.male)")
        }
    }
}

```
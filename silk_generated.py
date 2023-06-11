# -*- coding: utf-8 -*-
#
# TARGET arch is: ['-I/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include']
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 8
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



_libraries = {}
_libraries['libSKP_SILK_SDK.dylib'] = ctypes.CDLL('libSKP_SILK_SDK.dylib')
c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 8:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*8

def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))





class struct_c__SA_SKP_Silk_TOC_struct(Structure):
    pass

struct_c__SA_SKP_Silk_TOC_struct._pack_ = 1 # source:False
struct_c__SA_SKP_Silk_TOC_struct._fields_ = [
    ('framesInPacket', ctypes.c_int32),
    ('fs_kHz', ctypes.c_int32),
    ('inbandLBRR', ctypes.c_int32),
    ('corrupt', ctypes.c_int32),
    ('vadFlags', ctypes.c_int32 * 5),
    ('sigtypeFlags', ctypes.c_int32 * 5),
]

SKP_Silk_TOC_struct = struct_c__SA_SKP_Silk_TOC_struct
SKP_Silk_SDK_Get_Encoder_Size = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_Get_Encoder_Size
SKP_Silk_SDK_Get_Encoder_Size.restype = ctypes.c_int32
SKP_Silk_SDK_Get_Encoder_Size.argtypes = [ctypes.POINTER(ctypes.c_int32)]
class struct_c__SA_SKP_SILK_SDK_EncControlStruct(Structure):
    pass

struct_c__SA_SKP_SILK_SDK_EncControlStruct._pack_ = 1 # source:False
struct_c__SA_SKP_SILK_SDK_EncControlStruct._fields_ = [
    ('API_sampleRate', ctypes.c_int32),
    ('maxInternalSampleRate', ctypes.c_int32),
    ('packetSize', ctypes.c_int32),
    ('bitRate', ctypes.c_int32),
    ('packetLossPercentage', ctypes.c_int32),
    ('complexity', ctypes.c_int32),
    ('useInBandFEC', ctypes.c_int32),
    ('useDTX', ctypes.c_int32),
]

SKP_Silk_SDK_InitEncoder = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_InitEncoder
SKP_Silk_SDK_InitEncoder.restype = ctypes.c_int32
SKP_Silk_SDK_InitEncoder.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_c__SA_SKP_SILK_SDK_EncControlStruct)]
SKP_Silk_SDK_QueryEncoder = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_QueryEncoder
SKP_Silk_SDK_QueryEncoder.restype = ctypes.c_int32
SKP_Silk_SDK_QueryEncoder.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_c__SA_SKP_SILK_SDK_EncControlStruct)]
SKP_Silk_SDK_Encode = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_Encode
SKP_Silk_SDK_Encode.restype = ctypes.c_int32
SKP_Silk_SDK_Encode.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_c__SA_SKP_SILK_SDK_EncControlStruct), ctypes.POINTER(ctypes.c_int16), ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int16)]
SKP_Silk_SDK_Get_Decoder_Size = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_Get_Decoder_Size
SKP_Silk_SDK_Get_Decoder_Size.restype = ctypes.c_int32
SKP_Silk_SDK_Get_Decoder_Size.argtypes = [ctypes.POINTER(ctypes.c_int32)]
SKP_Silk_SDK_InitDecoder = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_InitDecoder
SKP_Silk_SDK_InitDecoder.restype = ctypes.c_int32
SKP_Silk_SDK_InitDecoder.argtypes = [ctypes.POINTER(None)]
class struct_c__SA_SKP_SILK_SDK_DecControlStruct(Structure):
    pass

struct_c__SA_SKP_SILK_SDK_DecControlStruct._pack_ = 1 # source:False
struct_c__SA_SKP_SILK_SDK_DecControlStruct._fields_ = [
    ('API_sampleRate', ctypes.c_int32),
    ('frameSize', ctypes.c_int32),
    ('framesPerPacket', ctypes.c_int32),
    ('moreInternalDecoderFrames', ctypes.c_int32),
    ('inBandFECOffset', ctypes.c_int32),
]

SKP_Silk_SDK_Decode = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_Decode
SKP_Silk_SDK_Decode.restype = ctypes.c_int32
SKP_Silk_SDK_Decode.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_c__SA_SKP_SILK_SDK_DecControlStruct), ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int16)]
SKP_Silk_SDK_search_for_LBRR = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_search_for_LBRR
SKP_Silk_SDK_search_for_LBRR.restype = None
SKP_Silk_SDK_search_for_LBRR.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int16)]
SKP_Silk_SDK_get_TOC = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_get_TOC
SKP_Silk_SDK_get_TOC.restype = None
SKP_Silk_SDK_get_TOC.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.POINTER(struct_c__SA_SKP_Silk_TOC_struct)]
SKP_Silk_SDK_get_version = _libraries['libSKP_SILK_SDK.dylib'].SKP_Silk_SDK_get_version
# SKP_Silk_SDK_get_version.restype = ctypes.POINTER(ctypes.c_char) # this is not correctly generated
SKP_Silk_SDK_get_version.restype = ctypes.c_char_p
SKP_Silk_SDK_get_version.argtypes = []
__all__ = \
    ['SKP_Silk_SDK_Decode', 'SKP_Silk_SDK_Encode',
    'SKP_Silk_SDK_Get_Decoder_Size', 'SKP_Silk_SDK_Get_Encoder_Size',
    'SKP_Silk_SDK_InitDecoder', 'SKP_Silk_SDK_InitEncoder',
    'SKP_Silk_SDK_QueryEncoder', 'SKP_Silk_SDK_get_TOC',
    'SKP_Silk_SDK_get_version', 'SKP_Silk_SDK_search_for_LBRR',
    'SKP_Silk_TOC_struct',
    'struct_c__SA_SKP_SILK_SDK_DecControlStruct',
    'struct_c__SA_SKP_SILK_SDK_EncControlStruct',
    'struct_c__SA_SKP_Silk_TOC_struct']

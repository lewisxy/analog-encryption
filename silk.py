"""Implement a nicer interface for python to use SILK library

silk_generated.py contains ctypes binding for SILK library generated
by ctypeslib2 (https://github.com/trolldbois/ctypeslib/issues)

Minor tweaks may be needed
"""

import ctypes
from dataclasses import dataclass

import silk_generated as silk

from typing import Literal, Optional

MAX_BYTES_PER_FRAME = 250
MAX_INPUT_FRAMES = 5
FRAME_LENGTH_MS = 20
MAX_API_FS_KHZ = 48

class SilkError(Exception):
    # TODO: implement errors
    pass

def Get_Encoder_Size() -> int:
    a = ctypes.c_int32()
    res = silk.SKP_Silk_SDK_Get_Encoder_Size(ctypes.byref(a))
    if res != 0:
        raise SilkError(res)
    assert a.value >= 0
    return a.value

def Get_Decoder_Size() -> int:
    a = ctypes.c_int32()
    res = silk.SKP_Silk_SDK_Get_Decoder_Size(ctypes.byref(a))
    if res != 0:
        raise SilkError(res)
    assert a.value >= 0
    return a.value

def get_version() -> str:
    res = silk.SKP_Silk_SDK_get_version()
    return res.decode("utf-8")

# raw_offset does not accomendate for the size of datastructure
# return type of None means no cast
def pointer_add(c_data, raw_offset, return_type=None):
    pv = ctypes.c_void_p(ctypes.addressof(c_data) + raw_offset)
    return ctypes.cast(pv, ctypes.POINTER(ctypes.c_short))

# return an array slice (no copy)
# type_ must be provided because there is no reliable way to infer type from the arr object
# start and end is in term of the element, not byte, element may have a size larger than byte
def array_slice(arr, type_, start, end=None):
    end = len(arr) if end is None else end
    length = end - start
    return (type_ * length).from_buffer(arr, ctypes.sizeof(type_) * start)

# return an array slice (copy)
def array_slice_copy(arr, type_, start, end=None):
    end = len(arr) if end is None else end
    length = end - start
    return (type_ * length).from_buffer_copy(arr, ctypes.sizeof(type_) * start)

@dataclass
class EncoderControl:
    sample_rate: Literal[8000, 12000, 16000, 24000] = 16000
    max_internal_sample_rate: Literal[8000, 12000, 16000, 24000] = 16000
    packet_size: int = 320 # Literal[20, 40, 60, 80, 100] * sample_rate / 1000
    bit_rate: int = 25000
    packet_loss_percentage: int = 0 # 0-100
    complexity: Literal[0, 1, 2] = 2
    use_inband_FEC: bool = False
    use_DTX: bool = False

    def to_cstruct(self) -> silk.struct_c__SA_SKP_SILK_SDK_EncControlStruct:
        return silk.struct_c__SA_SKP_SILK_SDK_EncControlStruct(
            self.sample_rate,
            self.max_internal_sample_rate,
            self.packet_size,
            self.bit_rate,
            self.packet_loss_percentage,
            self.complexity,
            1 if self.use_inband_FEC else 0,
            1 if self.use_DTX else 0,
        )

    @staticmethod
    def from_cstruct(s: silk.struct_c__SA_SKP_SILK_SDK_EncControlStruct) -> "EncoderControl":
        return EncoderControl(
            sample_rate = s.API_sampleRate,
            max_internal_sample_rate = s.maxInternalSampleRate,
            packet_size = s.packetSize,
            bit_rate = s.bitRate,
            packet_loss_percentage = s.packetLossPercentage,
            complexity = s.complexity,
            use_inband_FEC = False if s.useInBandFEC == 0 else True,
            use_DTX = False if s.useDTX == 0 else True,
        )


@dataclass
class DecoderControl:
    sample_rate: Literal[8000, 12000, 16000, 24000] = 16000
    frame_size: int = 0
    frames_per_packet: Literal[1, 2, 3, 4, 5] = 1
    more_internal_decoder_frames: bool = False
    inband_FEC_offset: int = 0

    def to_cstruct(self) -> silk.struct_c__SA_SKP_SILK_SDK_DecControlStruct:
        return silk.struct_c__SA_SKP_SILK_SDK_DecControlStruct(
            self.sample_rate,
            self.frame_size,
            self.frames_per_packet,
            1 if self.more_internal_decoder_frames else 0,
            self.inband_FEC_offset,
        )

    @staticmethod
    def from_cstruct(s: silk.struct_c__SA_SKP_SILK_SDK_DecControlStruct) -> "DecoderControl":
        return DecoderControl(
            sample_rate = s.API_sampleRate,
            frame_size = s.frameSize,
            frames_per_packet = s.framesPerPacket,
            more_internal_decoder_frames = False if s.moreInternalDecoderFrames == 0 else True,
            inband_FEC_offset = s.inBandFECOffset,
        )


class Encoder:
    def __init__(self):
        self.state = ctypes.create_string_buffer(Get_Encoder_Size())
        control = silk.struct_c__SA_SKP_SILK_SDK_EncControlStruct()
        self.control = EncoderControl.from_cstruct(control)
        res = silk.SKP_Silk_SDK_InitEncoder(ctypes.byref(self.state), ctypes.byref(control))
        if res != 0:
            raise SilkError(res)
        # self.output_buffer = ctypes.create_string_buffer(MAX_BYTES_PER_FRAME * MAX_INPUT_FRAMES)
        self.output_buffer = (ctypes.c_ubyte * (MAX_BYTES_PER_FRAME * MAX_INPUT_FRAMES))()

    def encode(self, samples, options: Optional[EncoderControl] = None):
        if options is None:
            options = self.control
        # TODO: maybe avoid copying by using numpy array with dtype=int16
        # print(samples)
        c_samples = (ctypes.c_int16 * len(samples))(*samples)
        # c_samples = (ctypes.c_int16 * (len(samples) // 2)).from_buffer_copy(samples)
        # output_size = ctypes.c_int16(len(self.output_buffer))
        output_size = ctypes.c_int16(MAX_BYTES_PER_FRAME * MAX_INPUT_FRAMES)
        # res = silk.SKP_Silk_SDK_Encode(ctypes.byref(self.state), ctypes.byref(options.to_cstruct()),
        #                                ctypes.byref(c_samples), len(c_samples),
        #                                ctypes.byref(self.output_buffer), ctypes.byref(output_size))
        res = silk.SKP_Silk_SDK_Encode(ctypes.byref(self.state), ctypes.byref(options.to_cstruct()),
                                       c_samples, len(c_samples),
                                       self.output_buffer, ctypes.byref(output_size))
        if res != 0:
            raise SilkError(res)
        
        # copy output
        # TODO: maybe use numpy array instead?
        # TODO: provide option to not copy the buffer (return array slice instead)
        return bytearray(self.output_buffer[:output_size.value])


class Decoder:
    def __init__(self, sample_rate: Literal[8000, 12000, 16000, 24000] = 16000) -> None:
        self.state = ctypes.create_string_buffer(Get_Decoder_Size())
        res = silk.SKP_Silk_SDK_InitDecoder(ctypes.byref(self.state))
        if res != 0:
            raise SilkError(res)
        self.output_buffer = (ctypes.c_int16 * (FRAME_LENGTH_MS * MAX_API_FS_KHZ * 2 * MAX_INPUT_FRAMES))()
        self.sample_rate = sample_rate
        self.control = DecoderControl(sample_rate=sample_rate).to_cstruct()

    # def decode(self, samples, lost=False):
    #     # TODO: maybe avoid copying by using numpy array with dtype=int8
    #     c_samples = (ctypes.c_ubyte * len(samples))(*samples)
    #     output_size = ctypes.c_int16(len(self.output_buffer))
    #     res = silk.SKP_Silk_SDK_Decode(ctypes.byref(self.state), ctypes.byref(self.control), lost,
    #                                    ctypes.byref(c_samples), len(c_samples),
    #                                    ctypes.byref(self.output_buffer), ctypes.byref(output_size))
    #     if res != 0:
    #         raise SilkError(res)
        
    #     # copy output
    #     # TODO: maybe use numpy array instead?
    #     # TODO: provide option to not copy the buffer (return array slice instead)
    #     return self.output_buffer[:output_size.value]
    
    def decode2(self, samples, lost=False):
        # TODO: maybe avoid copying by using numpy array with dtype=int8
        c_samples = (ctypes.c_ubyte * len(samples))(*samples)
        output_size = ctypes.c_int16(len(self.output_buffer))
        lost = 1 if lost else 0
        # create a shallow copy (slice) of output_buffer
        output_buffer_tmp = array_slice(self.output_buffer, ctypes.c_int16, 0)
        frames = 0
        total_size = 0
        while True:
            res = silk.SKP_Silk_SDK_Decode(ctypes.byref(self.state), ctypes.byref(self.control), lost,
                                        c_samples, len(c_samples),
                                        output_buffer_tmp, ctypes.byref(output_size))
            if res != 0:
                raise SilkError(res)
            # create new slice based on the returned value
            print(f"output_size: {output_size.value}")
            output_buffer_tmp = array_slice(output_buffer_tmp, ctypes.c_int16, output_size.value)
            frames += 1
            total_size += output_size.value
            if frames > MAX_INPUT_FRAMES:
                output_buffer_tmp = self.output_buffer
                frames = 0
                # this is likly an error condition
                print("!!!")
            if not DecoderControl.from_cstruct(self.control).more_internal_decoder_frames:
                print(frames) # 1
                break

        # print(f"total_decode_size: {total_size}")
        
        # copy output
        # TODO: maybe use numpy array instead?
        # TODO: provide option to not copy the buffer (return array slice instead)
        return array_slice_copy(self.output_buffer, ctypes.c_int16, 0, total_size)
        

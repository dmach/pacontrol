import abc
import struct
from typing import BinaryIO

from .util import unpack_from_stream


class PDU:
    """
    PDU stands for Protocol Data Unit.
    They are the building blocks of communication in the AES70 standard.
    """

    PDU_TYPE: int


class OcaType(abc.ABC):
    """
    None: 0
    OcaBoolean: 1
    OcaInt8: 2
    OcaInt16: 3
    OcaInt32: 4
    OcaInt64: 5
    OcaUint8: 6
    OcaUint16: 7
    OcaUint32: 8
    OcaUint64: 9
    OcaFloat32: 10
    OcaFloat64: 11
    OcaString: 12
    OcaBitstring: 13
    OcaBlob: 14
    OcaBlobFixedLen: 15
    OcaBit: 16
    """

    OCA_TYPE: int
    FORMAT: str

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    @classmethod
    def decode(cls, stream: BinaryIO):
        value = unpack_from_stream(cls.FORMAT, stream)[0]
        return cls(value)

    def encode(self):
        return struct.pack(self.FORMAT, self.value)


class OcaInt8(OcaType):
    OCA_TYPE = 2
    FORMAT = "!b"


class OcaInt16(OcaType):
    OCA_TYPE = 3
    FORMAT = "!h"


class OcaInt32(OcaType):
    OCA_TYPE = 4
    FORMAT = "!i"


class OcaUint8(OcaType):
    OCA_TYPE = 6
    FORMAT = "!B"


class OcaUint16(OcaType):
    OCA_TYPE = 7
    FORMAT = "!H"


class OcaUint32(OcaType):
    OCA_TYPE = 8
    FORMAT = "!I"


class OcaString(OcaType):
    OCA_TYPE = 12

    @classmethod
    def decode(cls, stream: BinaryIO):
        size = unpack_from_stream("!H", stream)[0]
        value = unpack_from_stream(f"!{size}s", stream)[0].decode("utf-8")
        return cls(value)

    def encode(self):
        result: bytes = b""

        value = self.value.encode("utf-8")
        size = len(value)

        # size
        result += struct.pack("!H", size)
        # value
        result += struct.pack(f"!{size}s", value)
        return result

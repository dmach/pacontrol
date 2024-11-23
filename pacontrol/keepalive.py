import struct
from typing import BinaryIO

from .types import PDU
from .util import unpack_from_stream


class Keepalive(PDU):
    PDU_TYPE = 4

    def __init__(self, timeout: int = 1):
        super().__init__()
        # the timeout values are a bit strange given the different 2 byte and 4 byte handling
        # TODO: clarify what the values mean and why we can use different uint sizes
        self.timeout = timeout

    @classmethod
    def decode(cls, stream: BinaryIO, size=4):
        if size == 4:
            value = unpack_from_stream("!I", stream)
        elif size == 2:
            value = unpack_from_stream("!H", stream) * 1000
        else:
            raise ValueError(f"Invalid keepalive timeout length: {size}")

        obj = cls(value)
        return obj

    def encode(self) -> bytes:
        # HACK
        return struct.pack("!H", self.timeout)

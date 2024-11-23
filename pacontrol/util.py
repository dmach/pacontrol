import struct
from typing import BinaryIO


def unpack_from_stream(fmt: str, stream: BinaryIO):
    """
    Unpack data from a binary stream (usually io.BytesIO)
    """
    size = struct.calcsize(fmt)
    data = stream.read(size)
    return struct.unpack(fmt, data)

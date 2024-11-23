import struct
from typing import BinaryIO

from .util import unpack_from_stream


class Message:
    SYNC = 0x3B
    FORMAT = "!BHIBH"

    def __init__(
        self,
        protocol_version: int,
        message_size: int,
        pdu_type: int,
        pdu_count: int,
    ):
        self.protocol_version = protocol_version
        self.message_size = message_size
        self.pdu_type = pdu_type
        self.pdu_count = pdu_count

    @classmethod
    def decode(cls, stream: BinaryIO) -> "Message":
        (
            sync,
            protocol_version,
            message_size,
            pdu_type,
            pdu_count,
        ) = unpack_from_stream(cls.FORMAT, stream)

        if sync != cls.SYNC:
            raise RuntimeError("Bad sync byte value.")

        return cls(protocol_version, message_size, pdu_type, pdu_count)

    def encode(self) -> bytes:
        result = struct.pack(
            self.FORMAT,
            self.SYNC,
            self.protocol_version,
            self.message_size,
            self.pdu_type,
            self.pdu_count,
        )
        return result

import io

import struct

from typing import BinaryIO
from typing import List

from .types import OcaType
from .types import PDU
from .util import unpack_from_stream


class Command(PDU):
    PDU_TYPE = 1
    FORMAT = "!IIIHHB"

    def __init__(
        self,
        handle,
        target,
        method_level: int,
        method_index: int,
        method_params: List[OcaType] | None = None,
    ):
        self.handle = handle
        self.target = target
        self.method_level = method_level
        self.method_index = method_index
        self.method_params = method_params or []

    @classmethod
    def decode(cls, stream: BinaryIO, method_params_types: List[type] = None):
        (
            encoded_length,
            handle,
            target,
            method_level,
            method_index,
            param_count,
        ) = unpack_from_stream(cls.FORMAT, stream)

        params = stream.read()
        stream = io.BytesIO(params)

        assert param_count == len(
            method_params_types
        ), f"Expected {param_count} parameters, have {len(method_params_types)}"
        method_params_types = method_params_types or []
        method_params = []
        for param_type in method_params_types:
            param = param_type.decode(stream)
            method_params.append(param)
        return cls(handle, target, method_level, method_index, method_params)

    def encode(self) -> bytes:
        encoded_params = b""
        for param in self.method_params:
            encoded_params += param.encode()

        size = struct.calcsize(self.FORMAT) + len(encoded_params)
        result = struct.pack(
            self.FORMAT,
            size,
            self.handle,
            self.target,
            self.method_level,
            self.method_index,
            len(self.method_params),
        )
        result += encoded_params
        return result

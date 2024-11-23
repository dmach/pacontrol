from typing import BinaryIO
from typing import List

from .types import OcaType
from .types import PDU
from .util import unpack_from_stream


class Response(PDU):
    PDU_TYPE = 3

    def __init__(
        self,
        handle,
        status_code: int,
        param_count: int,
        params: List[OcaType] | None = None,
    ):
        self.handle = handle
        self.status_code = status_code
        self.param_count = param_count
        self.params = params or []

    @classmethod
    def decode(cls, stream: BinaryIO, param_types: List[type] | None = None):
        length, handle, status_code, param_count = unpack_from_stream("!IIBB", stream)
        assert param_count == len(param_types)

        params = []
        for param_type in param_types:
            param = param_type.decode(stream)
            params.append(param)

        return cls(handle, status_code, param_count, params)

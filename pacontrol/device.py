import io
import socket
import struct
from typing import List

from .command import Command
from .keepalive import Keepalive
from .message import Message
from .response import Response
from .types import OcaInt8
from .types import OcaString
from .types import OcaUint16
from .types import PDU


class Device:
    def __init__(self, info):
        self.info = info
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @property
    def addr(self):
        return (self.ip, self.port)

    @property
    def ip(self):
        return socket.inet_ntoa(self.info.addresses[0])

    @property
    def port(self):
        return self.info.port

    def send_bytes(self, data: bytes):
        self.sock.sendto(data, self.addr)

    def receive_bytes(self) -> bytes:
        return self.sock.recvfrom(1024)[0]

    def send_pdus(self, pdus: List[PDU]):
        assert pdus, "List of PDUs must not be empty"

        # it seems all sent PDUs must be of the same type
        pdu_type = pdus[0].PDU_TYPE

        # PDUs
        encoded_pdus: bytes = b""
        for pdu in pdus:
            if pdu.PDU_TYPE != pdu_type:
                raise ValueError("All PDUs must have the same type")
            encoded_pdus += pdu.encode()

        message = Message(
            protocol_version=1,
            # we're substracting 1 for the sync byte
            message_size=struct.calcsize(Message.FORMAT) - 1 + len(encoded_pdus),
            pdu_type=pdu_type,
            pdu_count=len(pdus),
        )
        encoded_message = message.encode()

        self.send_bytes(encoded_message + encoded_pdus)

    def receive_response(self, param_types: List[type] | None = None):
        data = self.receive_bytes()
        stream = io.BytesIO(data)

        message = Message.decode(stream)

        assert message.pdu_type == Response.PDU_TYPE
        assert message.pdu_count == len(param_types)

        return Response.decode(stream, param_types)

    def send_keepalive(self):
        """
        Send keepalive packet.
        It also initializes communication with the device.
        """
        # TODO: both ends should agree on a keep alive interval
        self.send_pdus([Keepalive(timeout=3)])
        # TODO: verify that we've received a keepalive packet back
        self.receive_bytes()

    def blink(self):
        """
        Identify a device by blinking its diode
        """
        cmd = Command(
            handle=52,
            target=50593804,
            method_level=5,
            method_index=2,
            method_params=[OcaUint16(257)],  # 0x0101
        )
        self.send_pdus([cmd])

    def get_serial_number(self):
        """
        Get serial number
        """
        cmd = Command(
            handle=0,
            target=1,
            method_level=3,
            method_index=3,
        )
        self.send_pdus([cmd])

        response = self.receive_response([OcaString])
        return response.params[0].value

    def get_name(self):
        cmd = Command(
            handle=0,
            target=1,
            method_level=3,
            method_index=4,
        )
        self.send_pdus([cmd])

        response = self.receive_response([OcaString])
        return response.params[0].value

    def get_description(self):
        """
        Get description of the device.
        """
        cmd = Command(
            handle=0,
            target=50593843,
            method_level=5,
            method_index=1,
        )
        self.send_pdus([cmd])

        response = self.receive_response([OcaString])
        return response.params[0].value

    def set_description(self, value: str):
        """
        Set description of the speaker.
        Example: "A7V Left"
        """
        cmd = Command(
            handle=59,
            target=50593843,
            method_level=5,
            method_index=2,
            method_params=[OcaString(value)],
        )
        self.send_pdus([cmd])

    def set_sleep(self, value: bool):
        """
        Suspend the device.
        """
        cmd = Command(
            handle=0,
            target=50528364,
            method_level=4,
            method_index=2,
            method_params=[OcaUint16(int(value))],
        )
        self.send_pdus([cmd])

    def set_mute(self, value: bool):
        """
        Mute or unmute the device.
        """
        val = 5 if value else 1
        cmd = Command(
            handle=0,
            target=33619989,
            method_level=4,
            method_index=2,
            method_params=[OcaUint16(val)],
        )
        self.send_pdus([cmd])

    def set_input(self, value: int):
        """
        Select input:
            0: RCA
            1: XLR
        """
        assert value in (0, 1)
        cmd = Command(
            handle=0,
            target=16842763,
            method_level=4,
            method_index=2,
            method_params=[OcaUint16(value)],
        )
        self.send_pdus([cmd])

    def set_level(self, value: int):
        """
        Set volume level.
        Applicable to Ext. voicing.
        Signed integer values translate to 0.5 dB steps:
            -2 -> -1.0 dB
            -1 -> -0.5 dB
             0 ->  0.0 dB
             1 ->  0.5 dB
             2 ->  1.0 dB
        The range is limited in software to -20 dB to 6dB range (-40..12)
        """
        assert -40 <= value <= 12
        cmd = Command(
            handle=0,
            target=16842754,
            method_level=5,
            method_index=2,
            # TODO: A Control is capable of displaying finer resolution, sending 2 byte parameters
            method_params=[OcaInt8(value)],
        )
        self.send_pdus([cmd])

    def set_bass(self, value: int):
        """
        Set bass correction: -2, -1, 0, 1
        Applicable to Pure and UNR voicings.
        """
        assert -2 <= value <= 1
        cmd = Command(
            handle=0,
            target=50397285,
            method_level=5,
            method_index=2,
            method_params=[OcaInt8(value)],
        )
        self.send_pdus([cmd])

    def set_desk(self, value: int):
        """
        Set desk correction: -2, -1, 0
        Applicable to Pure and UNR voicings.
        """
        assert -2 <= value <= 0
        cmd = Command(
            handle=0,
            target=50397286,
            method_level=5,
            method_index=2,
            method_params=[OcaInt8(value)],
        )
        self.send_pdus([cmd])

    def set_presence(self, value: int):
        """
        Set presence correction: -1, 0, 1
        Applicable to Pure and UNR voicings.
        """
        assert -1 <= value <= 1
        cmd = Command(
            handle=0,
            target=50397287,
            method_level=5,
            method_index=2,
            method_params=[OcaInt8(value)],
        )
        self.send_pdus([cmd])

    def set_treble(self, value: int):
        """
        Set treble correction: -1, 0, 1
        Applicable to Pure and UNR voicings.
        """
        assert -1 <= value <= 1
        cmd = Command(
            handle=0,
            target=50397288,
            method_level=5,
            method_index=2,
            method_params=[OcaInt8(value)],
        )
        self.send_pdus([cmd])

    def set_voicing(self, value: int):
        """
        Set voicing:
         - 0: Pure (flat, highly accurate and neutral sounding option)
         - 1: UNR (Uniform Natural Response - dynamic, natural-sounding response curve)
         - 2: Ext. (Extended functionality when using the Advanced or Sonarworks calibrations)
        """
        assert value in (0, 1, 2)
        cmd = Command(
            handle=54,
            target=50397289,
            method_level=4,
            method_index=2,
            method_params=[OcaUint16(value)],
        )
        self.send_pdus([cmd])

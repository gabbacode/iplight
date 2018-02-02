import struct
import logging


class TlvProtocol:
    def __init__(self):
        self.head_size = 3
        self.command_handlers = {}

    def parse_head(self, raw_bytes):
        assert(len(raw_bytes) == self.head_size)

        command_code = raw_bytes[0]
        payload_length, = struct.unpack_from('>H', raw_bytes, 1)

        return command_code, payload_length

    def execute_command(self, command_code, payload_data):

        if command_code in self.command_handlers:
            logging.info("control protocol: executing handler for command %s...", command_code)
            self.command_handlers[command_code]\
                .execute(payload_data)
        else:
            logging.warning("control protocol: unknown command %s skipped", command_code)

    def register_command(self, code, command):
        self.command_handlers[code] = command

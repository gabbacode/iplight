import unittest
from iplight.protocol import TlvProtocol
from iplight.run_lamp_client_cli import LampTextView
from iplight.lamp import LampController


class TestControlProtocol(unittest.TestCase):

    def testCommandParsing(self):

        protocol = TlvProtocol()
        representation = LampTextView()
        lamp = LampController(protocol, representation)

        assert (3 == protocol.head_size)

        cmd, length = protocol.parse_head(b'\x12\x00\x00')
        protocol.execute_command(cmd, '')
        assert cmd == 18, "wrong command code {}".format(cmd)
        assert length == 0, "wrong length {}".format(length)
        assert lamp.lamp_state.is_on

        cmd, length = protocol.parse_head(b'\x13\x00\x00')
        protocol.execute_command(cmd, '')
        assert cmd == 19, "wrong command code {}".format(cmd)
        assert length == 0, "wrong length {}".format(length)
        assert not lamp.lamp_state.is_on

        cmd, length = protocol.parse_head(b'\x20\x00\x03')
        protocol.execute_command(cmd, b'\x10\x20\xFF')
        assert cmd == 32, "wrong command code {}".format(cmd)
        assert length == 3, "wrong length {}".format(length)
        assert lamp.lamp_state.color == '#1020FF'


if __name__ == '__main__':
    unittest.main()

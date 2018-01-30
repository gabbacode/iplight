import asyncio
import unittest
from iplight.run_lamp_client_cli import LampTextView
from iplight.lamp import LampController
from iplight.lamp_client import LampClient
from tests.iplight_server import ParrotServer


class TestIpCommunication(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.host = "127.0.0.1"
        self.port = 9999

    def testIpCommunication(self):

        loop = asyncio.new_event_loop()

        # make up dummy server
        server = ParrotServer(loop)
        server.start(self.host, self.port)

        # connecting to server
        lamp_client = LampClient(loop, self.host, self.port, 1)
        lamp_client_task = lamp_client.start()
        representation = LampTextView()
        LampController(lamp_client.protocol, representation)

        try:
            # wait until all stops
            loop.run_until_complete(
                asyncio.wait([
                    server.server_stopped_event.wait(),
                    lamp_client_task]))

            assert lamp_client.received_commands == 10
        finally:
            loop.close()

    def test_reconnect(self):

        loop = asyncio.new_event_loop()
        loop.debug = True

        # make up dummy server
        server = ParrotServer(loop)
        server.start(self.host, self.port)

        # connecting to server
        lamp_client = LampClient(loop, self.host, self.port, 5)
        lamp_client.start()
        representation = LampTextView()
        LampController(lamp_client.protocol, representation)

        try:
            # wait until server send all data and stop
            loop.run_until_complete(
                server.server_stopped_event.wait())

            # server must be stopped
            assert not server.is_server_running()

            # store count of commands received so far
            commands_count = lamp_client.received_commands

            # run server again
            server.start(self.host, self.port)

            # wait for server stops
            loop.run_until_complete(server.server_stopped_event.wait())

            loop.run_until_complete(lamp_client.stop_async())

            # now received commands counter MUST be greater
            assert commands_count < lamp_client.received_commands

            # now received commands counter MUST be greater
            assert lamp_client.received_commands == 20

        finally:
            loop.close()

    def test_partial_package_broken_head(self):

        loop = asyncio.new_event_loop()
        loop.debug = True

        # make up dummy server
        server = ParrotServer(loop)
        server.REPEAT_COUNT = 1
        server.REPEAT_PERIOD = 1
        server.COMMANDS = [
            b'\x20\x00\x03\x00\xFF',
            # missed byte
            b'\x00',
            # correct command
            b'\x20\x00\x03\x00\xFF\x00'
        ]
        server.start(self.host, self.port)

        try:
            # connecting to server
            lamp_client = LampClient(loop, self.host, self.port, 5)
            lamp_client_task = lamp_client.start()
            representation = LampTextView()
            LampController(lamp_client.protocol, representation)

            loop.run_until_complete(
                asyncio.wait([
                    server.server_stopped_event.wait(),
                    lamp_client_task]))

            # server must be stopped
            assert not server.is_server_running()

            commands_count = lamp_client.received_commands
            assert 2 == commands_count

        finally:
            loop.close()


if __name__ == '__main__':
    unittest.main()

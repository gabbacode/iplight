import asyncio
import logging
import threading
from iplight.protocol import TlvProtocol


class LampClient:

    READ_TIMEOUT = 5

    def __init__(self, loop, host, port, retry_count=0):
        self.loop = loop
        self.connection = None
        self.writer = None
        self.host = host
        self.port = port
        self.retry_count = retry_count
        self.received_commands = 0

        # this event checked in thread without lock
        self.is_closing_event = threading.Event()

        # this event is sets when client is finished
        self.is_closed_event = asyncio.Event(loop=self.loop)

        # just hard link to protocol
        self.protocol = TlvProtocol()

    async def tcp_client(self):

        self.connection = asyncio.open_connection(
            self.host,
            self.port,
            loop=self.loop)

        reader, self.writer = await self.connection

        try:
            while not reader.at_eof():

                if self.is_closing_event.is_set():
                    return

                head_data = await asyncio.wait_for(
                    reader.readexactly(self.protocol.head_size),
                    self.READ_TIMEOUT)

                command_code, payload_len = self.protocol.parse_head(head_data)

                payload_data = await asyncio.wait_for(
                    reader.readexactly(payload_len),
                    self.READ_TIMEOUT)

                self.protocol.execute_command(command_code, payload_data)

                self.received_commands += 1

                logging.debug('raw data received: %s', head_data + payload_data)

        finally:
            self.writer.close()
            self.connection.close()

    async def tcp_reconnect(self):
        address = '{} {}'.format(self.host, self.port)
        try_count = 0
        self.is_closed_event.clear()
        while True:
            if try_count > 0:
                await asyncio.sleep(2.0)

            logging.info('connecting to server %s...', address)
            try:

                await self.tcp_client()
                try_count = 0

            except ConnectionRefusedError:
                logging.warning('connection to server %s refused', address)
            except asyncio.TimeoutError:
                logging.warning('connection to server %s timed out', address)
            else:
                logging.warning('connection to server %s is closed.', address)

            # not lock just check if closing required
            if self.is_closing_event.is_set():
                break

            try_count += 1
            if self.retry_count != 0 and try_count >= self.retry_count:
                break

        self.is_closed_event.set()

    def start(self):
        # reset event to initial state
        self.is_closing_event.clear()
        return asyncio.Task(self.tcp_reconnect(), loop=self.loop)

    def stop(self):
        # request client to stop
        self.is_closing_event.set()
        self.connection.close()

    def stop_async(self):
        self.is_closing_event.set()
        self.connection.close()
        return self.is_closed_event.wait()

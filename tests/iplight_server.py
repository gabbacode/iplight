import asyncio
import logging

# ugly test server that repeat same commands continuously


class ParrotServer:

    REPEAT_PERIOD = 0.5

    REPEAT_COUNT = 2

    COMMANDS = [
        b'\x12\x00\x00',
        b'\x20\x00\x03\xFF\x00\x00',
        b'\x20\x00\x03\x00\xFF\x00',
        b'\x20\x00\x03\x00\x00\xFF',
        b'\x13\x00\x00',
    ]

    def __init__(self, loop):
        logging.basicConfig(level=logging.DEBUG)

        self.server = None
        self.loop = loop
        self.server_stopped_event = asyncio.Event(loop=self.loop)

    async def handle_client(self, client_reader, client_writer):

        logging.info("test server: client connected")

        c = self.REPEAT_COUNT

        while c > 0:
            c -= 1
            for cmd in range(len(self.COMMANDS)):
                logging.debug('test server: sending command to client %s', self.COMMANDS[cmd])
                client_writer.write(self.COMMANDS[cmd])
                await client_writer.drain()
                await asyncio.sleep(self.REPEAT_PERIOD)

        await asyncio.sleep(self.REPEAT_PERIOD)
        self.stop()

    def start(self, host, port):
        self.server = self.loop.run_until_complete(
            asyncio.start_server(
                self.handle_client,
                host,
                port,
                loop=self.loop))
        self.server_stopped_event.clear()
        logging.info("test server: started")

    def stop(self):
        if self.server is not None:
            self.server.close()
        self.server = None
        logging.info("test server: stopped")
        self.server_stopped_event.set()

    def is_server_running(self):
        return self.server is not None


if __name__ == '__main__':
    main_loop = asyncio.get_event_loop()

    host = "127.0.0.1"
    port = 9999

    server = ParrotServer(main_loop)
    server.start(host, port)

    try:
        main_loop.run_until_complete(server.server_stopped_event.wait())
    finally:
        main_loop.close()

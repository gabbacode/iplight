import asyncio
import signal
import sys
from iplight.arguments import get_arguments
from iplight.lamp import LampRepresentation
from iplight.lamp import LampController
from iplight.lamp_client import LampClient


class LampTextView(LampRepresentation):
    # used for output state to console

    def show(self, state):
        print(
            "lamp: switched {0}, color {1}"
            .format(
                "on" if state.is_on else "off",
                state.color))


class InterruptedExit(SystemExit):
    code = 1


def run_loop_able_to_break(loop, action):

    def _signal_handler():
        raise InterruptedExit()

    if signal is not None and sys.platform != 'win32':
        loop.add_signal_handler(signal.SIGINT, _signal_handler)
    try:
        action(loop)
    finally:
        if signal is not None and sys.platform != 'win32':
            loop.remove_signal_handler(signal.SIGINT)
        loop.close()


if __name__ == '__main__':
    args = get_arguments()

    main_loop = asyncio.get_event_loop()

    new_client = LampClient(main_loop, args.host, args.port, retry_count=args.retry_count)
    representation = LampTextView()
    lamp = LampController(new_client.protocol, representation)

    client_task = new_client.start()

    try:
        run_loop_able_to_break(
            main_loop,
            lambda x: x.run_until_complete(client_task))
    finally:
        main_loop.close()

import signal
import sys

class InterruptedExit(SystemExit):
    code = 1


def run_loop_able_to_break(loop, action):

    def _signal_handler():
        raise InterruptedExit()

    if signal is not None and sys.platform != 'win32':
        loop.add_signal_handler(signal.SIGINT, _signal_handler)
        loop.add_signal_handler(signal.SIGBREAK, _signal_handler)
    try:
        action(loop)
    finally:
        if signal is not None and sys.platform != 'win32':
            loop.remove_signal_handler(signal.SIGINT)
            loop.remove_signal_handler(signal.SIGBREAK)
        loop.close()
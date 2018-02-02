import asyncio
import logging
from copy import deepcopy
from iplight.arguments import get_arguments
from iplight.lamp import LampRepresentation
from iplight.lamp import LampState
from iplight.lamp import LampController
from iplight.lamp_client import LampClient

import threading
from queue import Queue
from tkinter import *


class IndicatorWindow:
    def __init__(self, args):

        self.args = args
        self.lamp_client = None

        self.receive_data_thread = None
        self.receive_data_loop = None

        self.root = Tk()
        self.root.title("iplight client")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.resizable(width=False, height=False)
        self.canvas = Canvas(self.root, width=300, height=150)
        self.canvas.grid(row=2, column=0, rowspan=2, columnspan=2)

        self.host_caption = Label(self.root, text="ip light server host:")
        self.host_caption.grid(row=0, column=0, padx=5, pady=5)
        self.host_entry = Entry(self.root, width=50)
        self.host_entry.insert(0, args.host)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_caption = Label(self.root, text="port:")
        self.port_caption.grid(row=1, column=0, padx=5, pady=5)
        self.port_entry = Entry(self.root, width=50)
        self.port_entry.insert(0, args.port)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)

        self.lamp_view = LampGuiView(self.root, self.canvas)
        self.connect_button = Button(
            self.root,
            text='Connect',
            command=self.connect)
        self.connect_button.grid(row=5, column=1, padx=5, pady=5, sticky="e")

        self.disconnect_button = Button(
            self.root,
            text='Disconnect',
            command=self.disconnect)
        self.disconnect_button.grid(row=5, column=2, padx=5, pady=5, sticky="e")

        self.lamp_view.show(LampState())

    def window_run(self):
        self.root.mainloop()

    def on_closing(self):
        self.disconnect()
        self.root.destroy()

    def _receive_data_loop(self, host, port, retries):
        self.loop = asyncio.new_event_loop()

        try:
            self.lamp_client = LampClient(self.loop, host, port, retry_count=retries)

            LampController(self.lamp_client.protocol, self.lamp_view)
            client_task = self.lamp_client.start()

            self.loop.run_until_complete(client_task)
        finally:
            self.loop.close()

    def connect(self):
        self.receive_data_thread = threading.Thread(
            target=self._receive_data_loop,
            args=(
                self.host_entry.get(),
                self.port_entry.get(),
                self.args.retry_count,
            ))

        self.receive_data_thread.start()

    def disconnect(self):
        if self.lamp_client is None:
            return

        self.lamp_client.stop()


class LampGuiView(LampRepresentation):
    # used for output state to gui

    def __init__(self, root, canvas):
        self.canvas = canvas
        self.root = root
        self.queue = Queue()
        self.root.bind('<<DataReceived>>', self._data_received)
        self.light = None

    def _data_received(self, s):
        # ui thread handler, called when data from background threads come
        try:
            state = self.queue.get_nowait()
            self.queue.task_done()
            self.make_light(
                is_on=state.is_on,
                color=state.color)
        except Exception as e:
            logging.warning("handle of event DataReceived failed %s", e)

    def show(self, state):
        try:
            # make copy, and put data
            self.queue.put(
                deepcopy(state))

            # kick ui thread
            self.root.event_generate('<<DataReceived>>', when='tail')
        except Exception as e:
            logging.warning("generation DataReceived of event failed %s", e)

    def make_light(self, is_on, color='gray'):

        if self.light is not None:
            self.canvas.delete(self.light)

        if is_on:
            self.light = self.canvas.create_oval(
                100, 25, 200, 120,
                outline=color,
                fill=color)
        else:
            self.light = None

        return self.light


def run_indicator_ui_thread(args):
    w = IndicatorWindow(args)
    w.window_run()


if __name__ == '__main__':
    cli_args = get_arguments()
    run_indicator_ui_thread(cli_args)

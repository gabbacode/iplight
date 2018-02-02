class LampState:
    def __init__(self):
        self.is_on = False
        self.color = "#000000"


class LampController:

    def __init__(self, protocol, lamp_representation):
        self.lamp_state = LampState()
        self.protocol = protocol
        self.lamp_representation = lamp_representation

        self.register_commands(protocol)

    def turn_on_the_light(self, data):
        self.lamp_state.is_on = True
        self.lamp_representation.show(self.lamp_state)

    def turn_off_the_light(self, data):
        self.lamp_state.is_on = False
        self.lamp_representation.show(self.lamp_state)

    def change_color(self, data):
        c = (data[0], data[1], data[2])
        self.lamp_state.color = self.int_to_hex_color(c)
        self.lamp_representation.show(self.lamp_state)

    def register_commands(self, protocol):
        cmd_on = LampCommandRunner(self.turn_on_the_light)
        protocol.register_command(0x12, cmd_on)

        cmd_off = LampCommandRunner(self.turn_off_the_light)
        protocol.register_command(0x13, cmd_off)

        cmd_change_color = LampCommandRunner(self.change_color)
        protocol.register_command(0x20, cmd_change_color)

    @staticmethod
    def int_to_hex_color(v):
        assert (len(v) == 3)
        return '#%02X%02X%02X' % v


class LampRepresentation:
    def show(self, state):
        pass


class LampCommandRunner:
    def __init__(self, handler):
        self.handler = handler

    def execute(self, data):
        self.handler(data)

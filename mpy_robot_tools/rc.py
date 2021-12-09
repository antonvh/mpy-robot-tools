from .bt import UARTPeripheral, UARTCentral, CONNECT_IMAGES
from .helpers import clamp_int
from micropython import const
from hub import display, Image
import struct
from machine import Timer

L_STICK_HOR = const(0)
L_STICK_VER = const(1)
R_STICK_HOR = const(2)
R_STICK_VER = const(3)
L_TRIGGER = const(4)
R_TRIGGER = const(5)
SETTING1 = const(6)
SETTING2 = const(7)
BUTTONS = const(8)

class RCReceiver(UARTPeripheral):
    def __init__(self, **kwargs):
        self.set_logo("00000:05550:05950:05550:00000")
        # The super init also calls on disconnect.
        super().__init__(**kwargs)
        self.buffer = bytearray(struct.calcsize("bbbbBBhhB"))

    def _on_disconnect(self, *data):
        display.show(self._CONNECT_ANIMATION, delay=100, wait=False, loop=True)
        super()._on_disconnect(*data)

    def _on_connect(self, *data):
        display.show(self.logo)
        # The delay is there to come after the char discovery phase.
        t = Timer(
            mode=Timer.ONE_SHOT,
            period=2000,
            callback=lambda x:self.write(repr(self.logo))
            )
        super()._on_connect(*data)

    def set_logo(self, logo_str):
        self.logo=Image(logo_str)
        self._CONNECT_ANIMATION = [img + self.logo for img in CONNECT_IMAGES]

    def button_pressed(self, button):
        # Test if any buttons are pressed on the remote
        if 0 < button < 9:
            return self.controller_state(BUTTONS) & 1 << button-1
        else:
            return False

    def controller_state(self, *indices):
        try:
            controller_state = struct.unpack("bbbbBBhhB", self.buffer)
        except:
            controller_state = [0]*9
        if indices:
            if len(indices) is 1:
                return controller_state[indices[0]]
            else:
                return [controller_state[i] for i in indices]
        else:
            return controller_state
        

class RCTransmitter(UARTCentral):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # An empty 9 long list. Order is important.
        self.controller_state = [0]*9

    def set_button(self, num, pressed):
        if 0 < num < 9:
            bitmask = 0b1 << (num-1)
            if pressed:
                self.controller_state[BUTTONS] |= bitmask
            else:
                self.controller_state[BUTTONS] &= ~bitmask

    def set_stick(self, stick, value):
        self.controller_state[stick] = clamp_int(value)

    def set_trigger(self, trig, value):
        self.controller_state[trig] = clamp_int(value,0,200)

    def set_setting(self, stick, value):
        self.controller_state[stick] = clamp_int(value, -2**15, 2**15)

    # Send data over the UART
    def transmit(self):
        value = struct.pack("bbbbBBhhB", *self.controller_state)
        self.write(value)
from . import UARTCentral, UARTPeripheral
import struct
from micropython import const
from time import ticks_ms, sleep_ms, ticks_diff

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
    """
    Class for an Remote Control Receiver. It reads and processes gamepad or remote control data.
    It will advertise as the given name.

    :param name: The name of this peripheral to advertise as. Default: "robot"
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    """
    def __init__(self, **kwargs):
        super().__init__(additive_buffer=False, **kwargs)
        self.read_buffer = bytearray(struct.calcsize("bbbbBBhhB"))

    def button_pressed(self, button):
        """
        Returns True if the given button is pressed on the remote control.

        :param button: The button number to check. 1-8
        :type button: int
        """
        if 0 < button < 9:
            return self.controller_state(BUTTONS) & 1 << button-1
        else:
            return False

    def controller_state(self, *indices):
        """
        Returns the controller state as a list of 9 integers: 
        [left_stick_x, left_stick_y, right_stick_x, right_stick_y, left_trigger, 
        right_trigger, left_setting, right_setting, buttons]

        :param indices: The items of the selection of controller states to return. 
            If omitted, the whole list is returned. Use these constants: 
            `L_STICK_HOR, L_STICK_VER, R_STICK_HOR, R_STICK_VER, L_TRIGGER, R_TRIGGER, 
            SETTING1, SETTING2, BUTTONS`
        
        :type indices: int

        Use the controller state L_STICK indices to get only left stick values::

            left_stick_x, left_stick_y, = rc.controller_state(L_STICK_HOR, L_STICK_VER)

        """
        try:
            controller_state = struct.unpack("bbbbBBhhB", self.read_buffer)
        except:
            controller_state = [0]*9
        if indices:
            if len(indices) == 1:
                return controller_state[indices[0]]
            else:
                return [controller_state[i] for i in indices]
        else:
            return controller_state


class RCTransmitter(UARTCentral):
    """
    Class for a Remote control transmitter. It sends gamepad or remote control data to a receiver.

    :param name: The name of the peripheral to search for and connect to. Default: "robot"
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # An empty 9-item list. Order is important.
        self.controller_state = [0]*9
        self.last_write = 0

    @staticmethod
    def clamp_int(n, floor=-100, ceiling=100):
        return max(min(round(n), ceiling), floor)

    def set_button(self, num, pressed):
        """
        Set a button to pressed or not pressed.

        :param num: The button number to set. 1-8
        :type num: int
        :param pressed: True or False
        :type pressed: bool
        """
        if 0 < num < 9:
            bitmask = 0b1 << (num-1)
            if pressed:
                self.controller_state[BUTTONS] |= bitmask
            else:
                self.controller_state[BUTTONS] &= ~bitmask

    def set_stick(self, stick, value):
        """
        Set a stick value. Value should be between -100 and 100.

        :param stick: The stick to set. Use these constants: L_STICK_HOR, L_STICK_VER, R_STICK_HOR, R_STICK_VER
        :type stick: int
        :param value: The value to set. Should be between -100 and 100.
        :type value: int
        """
        self.controller_state[stick] = self.clamp_int(value)

    def set_trigger(self, trig, value):
        """
        Set a gamepad shoulder trigger value. Value should be between 0 and 200.

        :param trig: The trigger to set. Use these constants: L_TRIGGER, R_TRIGGER
        :type trig: int
        :param value: The value to set. Should be between 0 and 200.
        :type value: int
        """
        self.controller_state[trig] = self.clamp_int(value,0,200)

    def set_setting(self, setting, value):
        """
        Set a parameter dial setting.

        :param setting: The setting to set. Use these constants: SETTING1, SETTING2
        :type setting: int
        :param value: The value to set. Should be between -32768 and 32767.
        :type value: int
        """
        self.controller_state[setting] = self.clamp_int(value, -2**15, 2**15)

    def transmit(self):
        """
        Send the controller state to the receiver.
        This call will wait if you write again within 15ms.
        """
        # Don't send too often.
        while ticks_diff(ticks_ms(), self.last_write) < 15:
            sleep_ms(1)
        value = struct.pack("bbbbBBhhB", *self.controller_state)
        self.fast_write(value)
        self.last_write = ticks_ms()
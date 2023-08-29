# Micropython i2c library for SEN0539-EN Voice Recognition Module by DFRobot
# DFRobot_DF2301Q Class infrastructure, implementation of underlying methods


from micropython import const
from time import sleep_ms
from sys import platform

ESP = const(0)
OPENMV = const(1)
PFRM = ESP
if "OpenMV" in platform:
    PFRM = OPENMV
    from pyb import I2C
    i2c4 = I2C(4, I2C.MASTER)
else:
    from machine import SoftI2C, Pin
    

## Address of the register for requesting command word ID
REG_GET_CMD_ID = const(0x02)
## Address of the register for playing audio by command word ID
REG_PLAY_CMD_ID = const(0x03)
## i2c address
SEN0539_I2C_ADDR = const(0x64)
## Register for setting mute mode
REG_SET_MUTE = const(0x04)
## Register for setting volume
REG_SET_VOLUME = const(0x05)
## Address of the register for wake-up time
REG_WAKE_TIME = const(0x06)

#: All command words and their IDs
CMD_IDS = {
    0: "Listening...",
    1: "Wake-up words for learning",
    2: "Hello robot",
    5: "The first custom command",
    6: "The second custom command",
    7: "The third custom command",
    8: "The fourth custom command",
    9: "The fifth custom command",
    10: "The sixth custom command",
    11: "The seventh custom command",
    12: "The eighth custom command",
    13: "The ninth custom command",
    14: "The tenth custom command",
    15: "The eleventh custom command",
    16: "The twelfth custom command",
    17: "The thirteenth custom command",
    18: "The fourteenth custom command",
    19: "The fifteenth custom command",
    20: "The sixteenth custom command",
    21: "The seventeenth custom command",
    22: "Go forward",
    23: "Retreat",
    24: "Park a car",
    25: "Turn left ninety degrees",
    26: "Turn left forty-five degrees",
    27: "Turn left thirty degrees",
    28: "Turn right ninety degrees",
    29: "Turn right forty-five degrees",
    30: "Turn right thirty degrees",
    31: "Shift down a gear",
    32: "Line tracking mode",
    33: "Light tracking mode",
    34: "Bluetooth mode",
    35: "Obstacle avoidance mode",
    36: "Face recognition",
    37: "Object tracking",
    38: "Object recognition",
    39: "Line tracking",
    40: "Color recognition",
    41: "Tag recognition",
    42: "Object sorting",
    43: "Qr code recognition",
    44: "General settings",
    45: "Clear screen",
    46: "Learn once",
    47: "Forget",
    48: "Load model",
    49: "Save model",
    50: "Take photos and save them",
    51: "Save and return",
    52: "Display number zero",
    53: "Display number one",
    54: "Display number two",
    55: "Display number three",
    56: "Display number four",
    57: "Display number five",
    58: "Display number six",
    59: "Display number seven",
    60: "Display number eight",
    61: "Display number nine",
    62: "Display smiley face",
    63: "Display crying face",
    64: "Display heart",
    65: "Turn off dot matrix",
    66: "Read current posture",
    67: "Read ambient light",
    68: "Read compass",
    69: "Read temperature",
    70: "Read acceleration",
    71: "Reading sound intensity",
    72: "Calibrate electronic gyroscope",
    73: "Turn on the camera",
    74: "Turn off the camera",
    75: "Turn on the fan",
    76: "Turn off the fan",
    77: "Turn fan speed to gear one",
    78: "Turn fan speed to gear two",
    79: "Turn fan speed to gear three",
    80: "Start oscillating",
    81: "Stop oscillating",
    82: "Reset",
    83: "Set servo to ten degrees",
    84: "Set servo to thirty degrees",
    85: "Set servo to forty-five degrees",
    86: "Set servo to sixty degrees",
    87: "Set servo to ninety degrees",
    88: "Turn on the buzzer",
    89: "Turn off the buzzer",
    90: "Turn on the speaker",
    91: "Turn off the speaker",
    92: "Play music",
    93: "Stop playing",
    94: "The last track",
    95: "The next track",
    96: "Repeat this track",
    97: "Volume up",
    98: "Volume down",
    99: "Change volume to maximum",
    100: "Change volume to minimum",
    101: "Change volume to medium",
    102: "Play poem",
    103: "Turn on the light",
    104: "Turn off the light",
    105: "Brighten the light",
    106: "Dim the light",
    107: "Adjust brightness to maximum",
    108: "Adjust brightness to minimum",
    109: "Increase color temperature",
    110: "Decrease color temperature",
    111: "Adjust color temperature to maximum",
    112: "Adjust color temperature to minimum",
    113: "Daylight mode",
    114: "Moonlight mode",
    115: "Color mode",
    116: "Set to red",
    117: "Set to orange",
    118: "Set to yellow",
    119: "Set to green",
    120: "Set to cyan",
    121: "Set to blue",
    122: "Set to purple",
    123: "Set to white",
    124: "Turn on ac",
    125: "Turn off ac",
    126: "Increase temperature",
    127: "Decrease temperature",
    128: "Cool mode",
    129: "Heat mode",
    130: "Auto mode",
    131: "Dry mode",
    132: "Fan mode",
    133: "Enable blowing up & down",
    134: "Disable blowing up & down",
    135: "Enable blowing right & left",
    136: "Disable blowing right & left",
    137: "Open the window",
    138: "Close the window",
    139: "Open curtain",
    140: "Close curtain",
    141: "Open the door",
    142: "Close the door",
    200: "Learning wake word",
    201: "Learning command word",
    202: "Re-learn",
    203: "Exit learning",
    204: "I want to delete",
    205: "Delete wake word",
    206: "Delete command word",
    207: "Exit deleting",
    208: "Delete all",
}


class SEN0539:
    """
    Class for SEN0539-EN Voice Recognition Module by DFRobot

    :param scl: SCL pin number, default 2
    :type scl: int
    :param sda: SDA pin number, default 26
    :type sda: int
    :param i2c: I2C object, default None creates a new one with the scl and sda pins. 
        If using OpenMV, it defaults to i2c on bus 4 (sda=P8, scl=P7)

    :type i2c: I2C
    :param addr: I2C address of SEN0539 sensor, default 0x64
    :type addr: int
    """

    def __init__(self, scl=2, sda=26, i2c=None, addr=SEN0539_I2C_ADDR):
        if i2c is None:
            if PFRM == OPENMV:
                i2c = i2c4
            else:
                i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self.i2c = i2c
        self.addr = addr

    def get_cmd_id(self):
        """
        Get the command word ID of the last identified command word

        :return: Command word ID
        :rtype: int
        """
        sleep_ms(20)  # Don't overload the sensor
        return self.rd(REG_GET_CMD_ID)

    def play_cmd_id(self, cmd_id):
        """
        Play the corresponding reply audio according to the command word ID in CMD_IDS
        Can enter wake-up state through ID-1 in I2C mode

        :param cmd_id: Command word ID
        :type cmd_id: int
        """
        self.wr(REG_PLAY_CMD_ID, cmd_id)
        sleep_ms(500)  # Don't overload the sensor

    def get_wake_time(self):
        """
        Get the wake duration, before sensor says "I'm off now" and
        you have to wake it again with the wake word.

        :return: The current set wake-up period in seconds
        :rtype: int
        """
        return self.rd(REG_WAKE_TIME)

    def set_wake_time(self, wake_time: int):
        """
        Set wake duration

        :param wake_time: Wake duration, range 0~255, unit: 1s
        :type wake_time: int
        """
        self.wr(REG_WAKE_TIME, wake_time)

    def set_volume(self, vol: int):
        """
        Set voice volume. 0 mutes.

        :param vol: Volume value 0 - 20
        :type vol: int
        """
        if vol == 0:
            self.set_mute_mode(1)
        else:
            self.set_mute_mode(0)
            sleep_ms(20)  # Don't overload the sensor
            self.wr(REG_SET_VOLUME, vol)

    def set_mute_mode(self, mode):
        """
        Set mute mode

        :param mode: Mute mode; set value 1: mute, 0: unmute
        :type mode: int
        """
        if mode:
            self.wr(REG_SET_MUTE, 1)
        else:
            self.wr(REG_SET_MUTE, 0)

    def rd(self, reg):
        """
        Read a register

        :param reg: Register address
        :type reg: int
        :return: Register value
        :rtype: int
        """
        if PFRM == OPENMV:
            return self.i2c.mem_read(1, self.addr, reg)[0]
        else:
            return self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        
    def wr(self, reg, val):
        """
        Write a register

        :param reg: Register address
        :type reg: int
        :param val: Register value
        :type val: int
        """
        val &= 0xFF  # Make sure it's 8 bits
        if PFRM == OPENMV:
            self.i2c.mem_write(val, self.addr, reg)
        else:
            self.i2c.writeto_mem(self.addr, reg, bytes([val]))
# This file is here for compatibility with older projects.
# It's better to import everything from bt and light
# Less imports = less memory consumption

from .btbricks import (
    UARTPeripheral,
    UARTCentral,
    RCReceiver,
    RCTransmitter,
    L_STICK_HOR,
    L_STICK_VER,
    R_STICK_HOR,
    R_STICK_VER,
    L_TRIGGER,
    R_TRIGGER,
    SETTING1,
    SETTING2,
    BUTTONS,
)

from .light import CONNECT_IMAGES

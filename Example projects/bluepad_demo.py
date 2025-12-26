# Test script for a direct gamepad connection to the SPIK or MINDSTORMS hub.
# Using an LMS-ESP32 board. Get the board here:
# https://antonsmindstorms.com/product/wifi-python-esp32-board-for-mindstorms/

# The LMS-ESP32 runs our fork of bluepad with uartremote
# Get the firmware here:
# https://github.com/antonvh/generic-lms-esp32-uart-fw

from projects.mpy_robot_tools.serialtalk import SerialTalk
from projects.mpy_robot_tools.serialtalk.mshub import MSHubSerial

ur = SerialTalk(MSHubSerial("D"), timeout=20)

while 1:
    ack, pad = ur.call("gamepad")
    print(ack, pad)

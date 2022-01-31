# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code connects to a robot running ble_uart_simple_peripheral.py
import sys
try:
    from micropython import const
    # _COLS = const(0x10): underscore saves memory by not posting const outside lib
except:
    # Polyfill. Maybe add a Final type?
    def const(arg):
        return arg

_SPIKE=const(0x05)
_MAC=const(0x06)

platforms = {
    'LEGO Learning System Hub':_SPIKE,
    'darwin':_MAC,
}
_platform = platforms[sys.platform]
del(platforms)

if _platform==_SPIKE:
    from projects.mpy_robot_tools.bt import UARTCentral
    from utime import sleep_ms
    ser = UARTCentral(buffered=True)
    ser.connect("laptop")

elif _platform==_MAC:
    from projects.mpy_robot_tools.uartremote import *
    #ser = UartRemote(port='/dev/tty.')
    #not working yet


for i in range(10):
    # Since serial devices can only send bytes, strings or bytearrays
    # We need to convert i with repr(). The inverse of repr is eval.
    ser.write(repr(i))
    print("Sent:", i)
    sleep_ms(200)
    print("Received:", eval( ser.read() ))
    sleep_ms(100)

ser.disconnect()
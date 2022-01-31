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
    # This code waits to until a ble central connects. 
    # You can test this with the MINDSTORMS BLE RC app
    # You can also use ble_uart_simple_central.py

    from projects.mpy_robot_tools.bt import UARTPeripheral
    from utime import sleep_ms
    from mindstorms import MSHub


    mshub = MSHub()
    ser = UARTPeripheral(name="robot", buffered=True)
    while not ser.is_connected():
        sleep_ms(100)

elif _platform==_MAC:
    from projects.mpy_robot_tools.uartremote import *
    #ser = UartRemote(port='/dev/tty.')
    #not working yet


while 1:
    if ser.is_connected():
        data = ser.read()
        if data:
            # Echo the data we got
            ser.write(data)
            # Unpack the bytes we got with eval and show the result
            mshub.light_matrix.write(eval(ser.read()))
        sleep_ms(100)
        # ser.buffer = None
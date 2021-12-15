# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code connects to a robot running ble_uart_simple_peripheral.py

from projects.mpy_robot_tools.bt import UARTCentral
from utime import sleep_ms

ser = UARTCentral(buffered=True)
ser.connect("robot")
for i in range(10):
   # Since serial devices can only send bytes, strings or bytearrays
   # We need to convert i with repr(). The inverse of repr is eval.
    ser.write(repr(i))
    print("Sent:", i)
    sleep_ms(200)
    print("Received:", eval( ser.read() ))
    sleep_ms(100)
ser.disconnect()
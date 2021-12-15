# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

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
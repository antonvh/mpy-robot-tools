# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code waits to until a ble central connects. 
# You can test this with the MINDSTORMS BLE RC app
# You can also use ble_uart_simple_central.py

from projects.mpy_robot_tools.bt import UARTPeripheral
from utime import sleep_ms

server = UARTPeripheral(name="server")
print("Waiting for connection")
while 1:
    if server.is_connected():
        data = server.readline()
        if data:
            print(data)
            server.write(data+b" echo\n")
    else:
        sleep_ms(200)
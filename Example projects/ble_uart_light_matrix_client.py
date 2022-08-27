# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code connects to a robot running ble_uart_simple_peripheral.py

from projects.mpy_robot_tools.bt import UARTCentral
from projects.mpy_robot_tools.light import codelines, matrix_2_image
from hub import button, display
from utime import sleep_ms
## Client/central code
client = UARTCentral()
client.connect(name="server")

mycodelines = codelines()

while True:
    image_matrix = next(mycodelines)
    image = matrix_2_image(image_matrix)
    display.show(image)
    client.writeline( repr(image) )
    sleep_ms(100)

client.disconnect()
print("Disconnected")
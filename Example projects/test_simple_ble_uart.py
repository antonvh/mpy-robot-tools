from projects.mpy_robot_tools.bt import UARTPeripheral
from time import sleep_ms

# you can test this with the MINDSTORMS BLE RC app

ser = UARTPeripheral(name="robot")
while not ser.is_connected():
   sleep_ms(100)

while ser.is_connected():
   print(ser.read())
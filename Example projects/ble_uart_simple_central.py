from projects.mpy_robot_tools.bt import UARTCentral
from utime import sleep_ms

ser = UARTCentral()
ser.connect("robot")
for i in range(10):
    ser.write(repr(i))
    print(i)
    sleep_ms(500)
ser.disconnect()
del ser
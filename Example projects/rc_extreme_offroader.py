from hub import port
from projects.mpy_robot_tools.bt import SmartHub
from time import sleep_ms

thub = SmartHub()
thub.connect()

for i in range(2000):
    thub.run_target("C", port.D.motor.get()[2])
    speed = port.C.motor.get()[2]
    thub.dc(1, -speed)
    thub.dc(2, -speed)
    sleep_ms(10)
thub.dc(1, 0)
thub.dc(2, 0)
thub.disconnect()
del thub
raise SystemExit
### Boilerplate code for animating robots
### Facilitates synchronzing different motor movements
### Author: Anton Mindstorms Hacks
### Source: https://antonsmindstorms.com/
### Tutorials: https://www.youtube.com/c/AntonsMindstormsHacks/

import utime
from projects.mpy_robot_tools.motor_sync import Mechanism, AMHTimer

### Boilerplate control loop here
motors = []
motor_functions = []
my_mechanism = Mechanism(motors, motor_functions)
my_mechanism.shortest_path_reset()
timer= AMHTimer()
while timer.time < 10000:
    my_mechanism.update_motor_pwms(timer.time)
    utime.sleep_ms(15)
my_mechanism.stop()

raise SystemExit
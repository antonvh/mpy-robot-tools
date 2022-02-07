from mpy_robot_tools.uartremote import *
from mpy_robot_tools.servo import Servo
from machine import Pin

class Servos():
    servos = {
        21: Servo(21),
        22: Servo(22),
        23: Servo(23),
        25: Servo(25),
    }

    def set_angles(self, angles:dict):
        for pin, angle in angles.items():
            if pin not in self.servos:
                self.servos[pin] = Servo(pin)
            self.servos[pin].angle(angle)

s = Servos()

ur = UartRemote()
ur.add_command(s.set_angles, format="repr", name="set_angles")

ur.loop()



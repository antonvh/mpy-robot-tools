#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from serialtalk.auto import SerialTalk

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()
st = SerialTalk(Port.S1)
lm = Motor(Port.B)
rm = Motor(Port.C)
db = DriveBase(lm,rm,62, 19*8)

# Write your program here.
ev3.speaker.beep()

while True:
    status, data = st.call('cam')
    if status == "err":
        print("Script not running on OpenMV or not connected to port S1")
        turn, speed = [0,0]
    else:
        turn, speed = data
    print(turn, speed)
    db.drive(speed, turn*1.5)
#!/usr/bin/env pybricks-micropython

# This program steers a basic robot with a driving base through voice commands.
# The robot has an OpenMV Cam H7 Plus mounted on top, in blob detection mode.
# A SEN0538 Voice Recognition Module is connected to the OpenMV Cam via I2c
# It uses the Serial Talk protocol to communicate with the OpenMV Cam.
# The OpenMV Cam detects a blob and sends the coordinates to the EV3.
# The EV3 drives towards the blob until it is close enough to fetch.
# Then, it waits for a voice command from the OpenMV Cam.

# Teach the "Fetch ball" trigger word to the SEN0538 Voice Recognition Module by saying
# "Learning command word" and then "Fetch ball" into the microphone.

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from st.auto import SerialTalk

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

# Create your objects here.
ev3 = EV3Brick()
st = SerialTalk(Port.S1)
mb = Motor(Port.B, Direction.COUNTERCLOCKWISE)
mc = Motor(Port.C, Direction.COUNTERCLOCKWISE)
md = Motor(Port.D) # Claw
db = DriveBase(mb, mc, 64, 140)

# Write your program here.
ev3.speaker.beep()
# Find the position where the claw is closed.
md.run_until_stalled(100)
md.reset_angle(0)
md.run_target(300, -80)
print(st.call("echo", "SerialTalk is ready.")[1])

FETCH = 1
LISTEN = 0
CLOSE_BLOB_PIXELS = 10000

mode = LISTEN


while True:
    if mode == FETCH:
        x, y, num_pixels = st.call("get_blob")[1]

        print(x, y, num_pixels)
        if y < 45:  # The blob is close enough to fetch.
            db.stop()
            md.run_time(500, 500, Stop.HOLD)
            db.straight(-db.distance())
            mode = LISTEN
        elif 0 < num_pixels < CLOSE_BLOB_PIXELS:
            db.drive(max((CLOSE_BLOB_PIXELS - num_pixels) * 0.02, 0), (150 - x) * -0.7)
        else:
            db.drive(0, 50)
    elif mode == LISTEN:
        ack, cmd = st.call("cmd")
        if ack == "cmdack":
            if cmd > 0:
                # print(cmd)
                if cmd == 22:
                    print("Fwd")
                    db.straight(50)
                if cmd == 5:
                    print("Fetch ball")
                    db.reset()
                    mode = FETCH
                elif cmd == 23:
                    print("Back")
                    db.straight(-50)
                elif cmd == 25:
                    print("Left 90")
                    db.turn(90)
                elif cmd == 26:
                    print("Left 45")
                    db.turn(45)
                elif cmd == 27:
                    print("Left 30")
                    db.turn(30)
                elif cmd == 28:
                    print("Right 90")
                    db.turn(-90)
                elif cmd == 29:
                    print("Right 45")
                    db.turn(-45)
                elif cmd == 30:
                    print("Right 30")
                    db.turn(-30)
                elif cmd == 141:
                    print("Open")
                    md.run_target(300, -80)
                elif cmd == 142:
                    print("Close")
                    md.run_time(500, 500, Stop.HOLD)
                elif cmd == 2:
                    print("OK")
                else:
                    print(cmd)
            # Wait until something new is said, avoid doubles.
            wait(500)

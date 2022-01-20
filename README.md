# Micropython robot tools #

This is a collection of classes and methods that help you to animate robots. They are specifically aimed at LEGO MINDSTORMS and SPIKE Prime robots, although the classes are abstract enough to be useful elsewhere. The functionality is documented inside the code. Here are just the main usages. For in-depth articles see my blog on [antonsmindstorms.com](https://antonsmindstorms.com). 

## Installation ##

Copy the code from the [install script](Installer/install_mpy_robot_tools.py) to an empty python project in the LEGO MINDSTORMS or LEGO SPIKE program. Then run it once.

UNPLUG The hub before it completes the restart after the script!!

## Overview of the library's ##

[motor_sync.py](mpy_robot_tools/motor_sync.py)
- AMHTimer() - This is a timer class that returns milliseconds by default. 
- Mechanism(motors, time_functions) - Calculates pwms based on motor functions.
- sine_wave(), linear(), linear_interpolation() - The function return functions for use in the Mechanism Class

[light.py](mpy_robot_tools/light.py)
- image_99(int) - Returns a 5x5 matrix display hub.Image to show numbers up to 99 in one screen.

[bt.py](mpy_robot_tools/bt.py)
- BLEHandler() - Base Bluetooth Low Energy handler
- UARTCentral() - Connects to UARTPeripheral and implements read() and write() like serial uart.
- UARTPeripheral() - Waits for a connection from UARTCentral and implements read() and write() like serial uart.

[rc.py](mpy_robot_tools/rc.py)

- Use the [MINDSTORMS Ble RC Anroid app](https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc) or another Smart Hub to [remote control your robot](https://gist.github.com/antonvh/1f1d9c563268b4a8e9e1d7297e62ad53) or [Hot Rod](https://gist.github.com/antonvh/88548d95e771043662f038de451e28f2)

Example
- RCReceiver() - Receives RC commands from the android app or RCTransmitter class.
``` python
rcv = RCReceiver(name="snake")
while rcv.is_connected():
    speed, turn, delay_setting = rcv.controller_state(R_STICK_VER, L_STICK_HOR, SETTING2)
```
- RCTransmitter() - Connects to an RCReceiver and transmits the state of 9 gamepad-like controls.
``` python
remote_control = RCTransmitter()
remote_control.connect(name="snake")
remote_control.set_stick(L_STICK_HOR, steer_angle )
remote_control.set_stick(R_STICK_VER, forward)
remote_control.transmit()
```

[rctrl_plus.py](mpy_robot_tools/ctrl_plus.py)

- SmartHub() - Connects to a Technic smart hub and is able to control connected devices and read the states of the IMU and connected motors.

[pyhuskylens.py](https://github.com/antonvh/LEGO-HuskyLenslib/blob/master/Library/pyhuskylens.py)

- HuskyLens() - [Connect to Huskylens](https://github.com/antonvh/LEGO-HuskyLenslib) over a serial port and get Image AI data.

[helpers.py](mpy_robot_tools/helpers.py)

- clamp_int(n) - returns an an int between -100 and 100, clamping higher or lower numbers.
- scale(n, (source_min, source_max), (target_min, target_max)) - Returns a number scaled to a different range of numbers

[uartremote.py](https://github.com/antonvh/UartRemote/blob/master/MicroPython/uartremote.py)

- see https://github.com/antonvh/UartRemote

## To Do ##
- Please fork and help out this project by adding documentation. Could be docstrings, README or tutorials.

### Stubs ###
For programming convenience in VS Code I would love to collect stubs of all LEGO hub libraries. I've been looking into micropython-stubber but it didn't work for me.

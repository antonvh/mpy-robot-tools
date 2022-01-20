# Micropython robot tools #

This is a collection of classes and methods that help you to animate robots. They are specifically aimed at LEGO MINDSTORMS and SPIKE Prime robots, although the classes are abstract enough to be useful elsewhere. The functionality is documented inside the code. Here are just the main usages. For in-depth articles see my blog on [antonsmindstorms.com](https://antonsmindstorms.com). 

## Installation ##

Copy the code from the [install script](Installer/install_mpy_robot_tools.py) to an empty python project in the LEGO MINDSTORMS or LEGO SPIKE program. Then run it once.

UNPLUG The hub before it completes the restart after the script!! Watch the console output for action to unplug.

Caution if the Spike/Mindstorm app asks for a firmewae update and you accept you will need to re-install. You can just disconect and ignore the update the Hub will be in a "big square" for waiting for update just long press the center button and power cycle the hub to reconect to the lego app, it wont ask a second time to update in the instance.

### Uninstall ###

To uninstall reboot the lego hub and the lego Spike/Mindstorm app it will ask to update this will remove the tools.

## Overview of the tools ##

### motor_sync ###
- AMHTimer() - This is a timer class that returns milliseconds by default. 
- Mechanism(motors, time_functions) - Calculates pwms based on motor functions.
- sine_wave(), linear(), linear_interpolation() - The function return functions for use in the Mechanism Class

### light_matrix ###
- image_99(int) - Returns a 5x5 matrix display hub.Image to show numbers up to 99 in one screen.

### bt ###
- BLEHandler() - Base Bluetooth Low Energy handler
- UARTCentral() - Connects to UARTPeripheral and implements read() and write() like serial uart.
- UARTPeripheral() - Waits for a connection from UARTCentral and implements read() and write() like serial uart.

### rc ###
Use the [MINDSTORMS Ble RC Anroid app]() or another Smart Hub to remote control your robot.

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

### ctrl_plus ###
- SmartHub() - Connects to a Technic smart hub and is able to control connected devices and read the states of the IMU and connected motors.

### pyhuskylens ###
- HuskyLens() - Connect to Huskylens over a serial port and get Image AI data.

### helpers ###
- clamp_int(n) - returns an an int between -100 and 100, clamping higher or lower numbers.
- scale(n, (source_min, source_max), (target_min, target_max)) - Returns a number scaled to a different range of numbers

## To Do ##
### Documentation ###
Please fork and help out this project by adding documentation. Could be docstrings, README or tutorials.

### Stubs ###
For programming convenience in VS Code I woul love to collect stubs of all LEGO hub libraries. I've been looking into micropython-stubber but it didn't work for me.

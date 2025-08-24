# Micropython robot tools #

This is a collection of classes and methods that help you to animate robots. They are specifically aimed at LEGO MINDSTORMS and SPIKE Prime robots, although the classes are abstract enough to be useful elsewhere. The functionality is documented inside the code. Here are just the main usages. For in-depth articles see my blog on [antonsmindstorms.com](https://antonsmindstorms.com).

## Installation ##

1. Copy the code from the [install script](Installer/install_mpy_robot_tools.py) ([click the Copy raw contents button](https://github.blog/changelog/2021-09-20-quickly-copy-the-contents-of-a-file-to-the-clipboard/))  to an empty python project in the LEGO MINDSTORMS or LEGO SPIKE program.
2. Then run it once, it will take additional time to transfer to the Hub please use patience.
3. UNPLUG The hub before it completes the restart after the script!! Watch the console output for action to unplug.

Caution if the Spike/Mindstorm app asks for a firmware update, and you accept you will need to re-install. You can just disconnect and ignore the update the Hub will be in a "big square" for waiting for update just long press the center button and power cycle the hub to reconect to the lego app, it won't ask a second time to update in the instance.

### Uninstall ###

To uninstall remove the directory out of the /projects folder using a script, or something like ThonnyIDE File manager. 

To factory reset your hub to factory settings, using LEGO app, press the Hub Connection Icon on the Programming Canvas, press the More Button (···) in the Dashboard tab and select Reset Settings. Press OK to confirm the reset, or Cancel to keep the current settings. Be careful - resetting your Hub will delete all of your programs, and they can’t be recovered!

## Overview of the libraries ##

### motor_sync.py ###

- AMHTimer() - This is a timer class that returns milliseconds by default.
- Mechanism(motors, time_functions) - Calculates pwms based on motor functions.
- sine_wave(), linear(), linear_interpolation() - The function return functions for use in the Mechanism Class

### light.py ###

- image_99(int) - Returns a 5x5 matrix display hub.Image to show numbers up to 99 in one screen.

### bt.py ###

- BLEHandler() - Base Bluetooth Low Energy handler
- UARTCentral() - Connects to UARTPeripheral and implements read() and write() like serial uart.
- UARTPeripheral() - Waits for a connection from UARTCentral and implements read() and write() like serial uart.

By default the UART objects are buffered. They will remember everything ever written to them and you should flush their buffer with `_ = read()` to start clean. For remote control and state communication the buffer gets in the way. You just want to read the most recent state when it arrives. In that case initialize with `additive_buffer=False`
Example:

``` python
# Create link to the snake head, and advertise self as tail.
head_link = UARTPeripheral(name="tail", additive_buffer=False)
```

If you have multiple Bluetooth objects, like a remote control, a serialtalk and a plain UART, you need to pass a single BLEHandler to all of them:

``` python
from projects.mpy_robot_tools.bt import BLEHandler, UARTCentral
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR, SETTING2

ble = BLEHandler()
seg_1_link = UARTCentral(ble_handler=ble)
seg_2_link = UARTCentral(ble_handler=ble)
rcv = RCReceiver(name="snake", ble_handler=ble)
```


### rc.py ###

- Use the [MINDSTORMS Ble RC Anroid app](https://play.google.com/store/apps/details?id=com.antonsmindstorms.mindstormsrc) or another Smart Hub to [remote control your robot](https://gist.github.com/antonvh/1f1d9c563268b4a8e9e1d7297e62ad53) or [Hot Rod](https://gist.github.com/antonvh/88548d95e771043662f038de451e28f2)

- Example

  ``` python
  # RCReceiver() - Receives RC commands from the android app or RCTransmitter class.
  rcv = RCReceiver(name="snake")
  while rcv.is_connected():
      speed, turn, delay_setting = rcv.controller_state(R_STICK_VER, L_STICK_HOR, SETTING2)
  ```

  ``` python
  # RCTransmitter() - Connects to an RCReceiver and transmits the state of 9 gamepad-like controls.
  remote_control = RCTransmitter()
  remote_control.connect(name="snake")
  remote_control.set_stick(L_STICK_HOR, steer_angle )
  remote_control.set_stick(R_STICK_VER, forward)
  remote_control.transmit()
  ```

### rctrl_plus.py ###

- SmartHub() - Connects to a Technic smart hub and is able to control connected devices and read the states of the IMU and connected motors.

### pyhuskylens.py ###

- HuskyLens() - [Connect to Huskylens](https://github.com/antonvh/LEGO-HuskyLenslib) over a serial port and get Image AI data.
- clamp_int(n) - returns an an int between -100 and 100, clamping higher or lower numbers.

### helpers.py ###

- clamp_int(n) - returns an an int between -100 and 100, clamping higher or lower numbers.
- scale(n, (source_min, source_max), (target_min, target_max)) - Returns a number scaled to a different range of numbers

### Remote UART library: uartremote.py ###

NOTE: This is temporary. In the future I hope to replace with [serialtalk](https://github.com/antonvh/SerialTalk). It's the same idea but it also works over bluetooth and websockets.
This is a library for robust, near real-time communication between two UART devices. We developed it with LEGO EV3, SPIKE Prime and other MicroPython (ESP) modules. The library has the following properties:
- It is fast enough to read sensor data at 30-50Hz.
- It is fully symmetrical, so master and slave can have the same import.
- It includes a RAW REPL mode to upload code to a slave module. This means you can develop code for both modules in one file.
- It is implemented in MicroPython and Arduino/C code. With arduino code, much higher sensor reading speeds are possible, but flashing is a bit less user friendly.
- The library has a command loop to wait and listen for calls. That loop is customizable and non-blocking so you can add your own code to it.
- The C-struct-like encoding is included in the payload, so the other side always knows how to decode it.

Read more in the [README file of that library.](Submodules/UartRemote/README.md)

## To Do ##

- Please fork and help out this project by adding documentation. Could be docstrings, README or tutorials.

### Stubs ###

For programming convenience in VS Code I would love to collect stubs of all LEGO hub libraries. I've been looking into micropython-stubber but it didn't work for me.

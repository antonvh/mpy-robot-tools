<div align="center">
<img alt="mpy-robot-tools logo" src="https://raw.githubusercontent.com/antonvh/mpy-robot-tools/master/Images/mpy_robot_tools.png" width="200">

# mpy-robot-tools

[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE.md)
[![MicroPython](https://img.shields.io/badge/MicroPython-compatible-orange.svg)](https://micropython.org/)
[![LEGO](https://img.shields.io/badge/LEGO-SPIKE%20%7C%20MINDSTORMS-yellow.svg)](https://education.lego.com/)

A comprehensive collection of MicroPython libraries and tools for building advanced LEGO robots. Designed for **LEGO SPIKE Prime**, **MINDSTORMS Robot Inventor**, and **ESP32-based** robotics projects.

</div>

Create synchronized motor movements, advanced animations, remote control systems, and more with this powerful robotics toolkit. For in-depth articles and tutorials, visit [antonsmindstorms.com](https://antonsmindstorms.com).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Libraries](#core-libraries)
- [Example Projects](#example-projects)
- [Documentation](#documentation)
- [Supported Platforms](#supported-platforms)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Features

- 🎮 **Remote Control**: BLE RC transmitter/receiver with gamepad-like controls via [btbricks](https://github.com/antonvh/btbricks)
- ⚙️ **Motor Synchronization**: Advanced motor coordination with animation curves and timing functions
- 🎨 **LED Animations**: Display utilities for hub LEDs and 5x5 matrix displays
- 🔌 **SerialTalk**: Symmetrical UART/BLE/WebSocket communication for multi-hub projects
- 🤖 **Pybricks-like API**: Familiar interface for SPIKE/MINDSTORMS hubs with SI units
- 🎯 **HuskyLens Integration**: AI vision sensor support for object recognition and tracking
- 🛠️ **Helper Utilities**: Scaling, clamping, interpolation, and timing functions
- 📡 **Multiple Communication Protocols**: BLE UART, LEGO Protocol, SerialTalk, and more

## Installation

### On SPIKE Prime / MINDSTORMS Robot Inventor

1. Copy the code from the [install script](Installer/install_mpy_robot_tools.py) ([use the Copy raw contents button](https://github.blog/changelog/2021-09-20-quickly-copy-the-contents-of-a-file-to-the-clipboard/))
2. Paste into an empty Python project in the LEGO SPIKE/MINDSTORMS app
3. Run the script once (installation takes ~1 minute)
4. **IMPORTANT**: Watch the console output and unplug the hub when prompted before restart completes

> **Note**: If the app requests a firmware update, you can safely ignore it. Accepting the update will require reinstallation. To exit the update prompt, long-press the center button and power cycle the hub.

### Uninstall

To uninstall, remove the `/projects/mpy_robot_tools/` directory using a script or file manager (like Thonny IDE).

For a complete factory reset: In the LEGO app, click **Hub Connection Icon** → **More (···)** → **Reset Settings** → **OK**.

⚠️ **Warning**: Factory reset deletes all programs permanently!

## Quick Start

### Synchronized Motor Animation

```python
from projects.mpy_robot_tools.motor_sync import Mechanism, linear_interpolation
from projects.mpy_robot_tools.pybricks import Motor, Port

# Define motors
left = Motor(Port.A)
right = Motor(Port.B)

# Create animation with keyframes: (time_ms, angle_degrees)
movement = linear_interpolation([
    (0, 0),
    (1000, 180),
    (2000, 0)
])

# Run synchronized mechanism
mech = Mechanism([left, right], [movement, movement])
mech.start_loop(duration=2000)
```

### Remote Control Robot

```python
from projects.mpy_robot_tools.rc import RCReceiver, R_STICK_VER, L_STICK_HOR
from projects.mpy_robot_tools.pybricks import Motor, Port

# Setup motors and RC receiver
left_motor = Motor(Port.A)
right_motor = Motor(Port.B)
rcv = RCReceiver(name="myrobot")

print("Waiting for RC connection...")
while True:
    if rcv.is_connected():
        # Get joystick values (-100 to 100)
        throttle = rcv.controller_state(R_STICK_VER)
        steering = rcv.controller_state(L_STICK_HOR)
        
        # Tank drive control
        left_motor.dc(throttle + steering)
        right_motor.dc(throttle - steering)
```

### Display Number on Hub LED Matrix

```python
from projects.mpy_robot_tools.light import image_99
from hub import display

# Display numbers up to 99 on the 5x5 matrix
display.show(image_99(42))
```

### Multi-Hub Communication with SerialTalk

```python
from projects.mpy_robot_tools.serialtalk import SerialTalk
from hub import port

# Initialize SerialTalk on a UART port
talk = SerialTalk(port.A)

# Define a callable function
@talk.call
def set_motor_speed(speed):
    print(f"Setting motor to {speed}")
    # Your motor control code here

# Main loop - handle incoming commands
while True:
    talk.process()  # Non-blocking command processor
```

## Core Libraries

### motor_sync.py

Advanced motor synchronization and animation system.

- **`Mechanism(motors, time_functions)`** - Synchronizes multiple motors using time-based functions
- **`linear_interpolation(keyframes)`** - Creates smooth motion between keyframes
- **`sine_wave(amplitude, period)`** - Generates sinusoidal motion
- **`AMHTimer()`** - High-precision millisecond timer

### pybricks.py

Pybricks-compatible API for SPIKE Prime and MINDSTORMS Robot Inventor.

- **`Motor(port)`** - Motor control with encoders, SI units, and async support
- **`Port`** - Port definitions (A, B, C, D, E, F)
- **`wait(ms)`** - Millisecond-precision wait function
- **`UltrasonicSensor(port)`** - Distance sensing in mm/cm

### btbricks (submodule)

Bluetooth Low Energy communication library. See [btbricks documentation](https://github.com/antonvh/btbricks) for full API.

- **`UARTCentral()`** / **`UARTPeripheral()`** - Nordic UART Service for hub-to-hub communication
- **`RCReceiver()`** / **`RCTransmitter()`** - Remote control with gamepad interface
- **`MidiController()`** - Send MIDI over BLE
- **`BtHub()`** - Control LEGO hubs via Bluetooth

### serialtalk/

Symmetrical communication protocol for UART, BLE, and WebSocket connections.

- **`SerialTalk(port)`** - Remote procedure calls between devices
- **`@talk.call`** - Decorator to expose functions for remote calling
- Supports UART, Bluetooth, and WebSocket transports
- Non-blocking command processing loop

### light.py

LED display utilities for SPIKE/MINDSTORMS hubs.

- **`image_99(number)`** - Display 0-99 on 5x5 LED matrix
- **`CONNECT_IMAGES`** - Animation frames for connection indicators
- Custom image utilities and display helpers

### helpers.py

General utility functions.

- **`clamp_int(n, floor, ceiling)`** - Limit values to a range
- **`scale(val, src_range, dst_range)`** - Map values between ranges
- **`wait_until(func, condition)`** - Conditional waiting

### pyhuskylens.py

[HuskyLens](https://wiki.dfrobot.com/HUSKYLENS_V1.0_SKU_SEN0305_SEN0336) AI vision sensor integration.

- **`HuskyLens(port)`** - Object detection, face recognition, line tracking, etc.
- **`get_blocks()`** / **`get_arrows()`** - Retrieve detected objects
- Supports all HuskyLens algorithms

## Example Projects

The `Example projects/` directory contains fully working examples:

- **`rc_hotrod_car_receiver.py`** - RC car with BLE remote control
- **`rc_snake.py`** - Multi-segment robot snake with synchronized movement
- **`huskylens_demo.py`** - AI vision-based object tracking
- **`ble_uart_simple_central.py`** / **`ble_uart_simple_peripheral.py`** - Hub-to-hub communication
- **`bluepad_mecanum_wheels.py`** - Mecanum drive with gamepad control
- **`inventor_ble_midi_guitar.py`** - MIDI instrument using hub sensors

Browse the [Example projects](Example%20projects/) folder for more inspiration!

## Documentation

### Full API Reference

Comprehensive documentation is available at:

**[docs.antonsmindstorms.com](https://docs.antonsmindstorms.com/)**

### In-Code Documentation

All classes and functions include detailed docstrings. Use `help()` in the REPL:

```python
from projects.mpy_robot_tools.motor_sync import Mechanism
help(Mechanism)
```

### Tutorials and Articles

Visit [antonsmindstorms.com](https://antonsmindstorms.com) for:

- Step-by-step tutorials
- Advanced techniques
- Building instructions
- Video demonstrations

## Supported Platforms

- **LEGO SPIKE Prime** (all versions)
- **LEGO MINDSTORMS Robot Inventor** (51515)
- **LEGO SPIKE Essential** (limited support)
- **ESP32** with MicroPython (via [LMS-ESP32 board](https://antonsmindstorms.com/product/wifi-python-esp32-board-for-mindstorms/))
- Other MicroPython boards with compatible peripherals

## Contributing

Contributions are welcome! Help improve this project by:

- 📝 Adding documentation, docstrings, or tutorials
- 🐛 Reporting bugs or issues
- ✨ Submitting new features or examples
- 🔧 Improving existing code

Please fork the repository and submit pull requests.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE.md](LICENSE.md) for full details.

## Author

**Anton Vanhoucke**

- Website: [antonsmindstorms.com](https://antonsmindstorms.com)
- GitHub: [@antonvh](https://github.com/antonvh)

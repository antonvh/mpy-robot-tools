import hub
import utime

# pass_through(usb, uart) script to run on SPIKE. Use paste mode.
# On openMV, Go into the IDE, select the config openmv cam option under tools, 
# and then clock the enable repl on uart button and click save, 
# then restart the board and repl will be there.
# Note that you should reboot the SPIKE to get out of this script.
# Or start this script with the play button in openmv ide:
"""
from machine import UART
import os
uart = UART(3, 115200)
os.dupterm(uart)
"""

uart = hub.port.E
uart.mode(1)
utime.sleep_ms(1000)
uart.baud(115200)

usb = hub.USB_VCP(0)
usb.setinterrupt(-1)

while True:
    data = usb.read(256)
    if data:
        _ = uart.write(data)
    data = uart.read(256)
    if data:
        _ = usb.write(data)

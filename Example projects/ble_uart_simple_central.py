# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code connects to a robot running ble_uart_simple_peripheral.py

from projects.mpy_robot_tools.bt import UARTCentral

## Client/central code
client = UARTCentral()
client.connect(name="server")

for i in range(1, 40):
    msg = "Hello there!"*(i)
    client.write(str(len(msg))+" "+msg+"\n")
    answer = client.readline()
    print(answer[:10],answer[-10:])

client.disconnect()
print("Disconnected")
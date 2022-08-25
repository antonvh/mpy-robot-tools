# Author: Anton's Mindstorms (Anton Vanhoucke)
# https://antonsmindstorms.com

# This code connects to a robot running ble_uart_simple_peripheral.py

from projects.mpy_robot_tools.bt import UARTCentral

## Client/central code
client = UARTCentral()
client.connect(name="server")

try:
    # Send increasingly long messages to test message size
    for i in range(1, 40):
        msg = "Hello there!"*(i)
        client.write(str(len(msg))+" "+msg+"\n")
        answer = client.readline()
        print(answer[:10],answer[-10:])

except Exception as e:
    # Except errors so we can always disconnect after a programming mistake
    # If the ble stack hangs connected, you have to remove
    # the hub's battery.
    print(e)

client.disconnect()
print("Disconnected")
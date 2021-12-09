from time import sleep_ms

from mindstorms import MSHub
# you can test this with the MINDSTORMS BLE RC app

mshub = MSHub()
ser = UARTPeripheral(name="robot")
while not ser.is_connected():
    sleep_ms(100)

while 1:
    if ser.is_connected():
        mshub.light_matrix.write(eval(ser.read()))
        sleep_ms(10)
        # ser.buffer = None
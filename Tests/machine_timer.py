from machine import Timer
from utime import sleep_ms

t = Timer()

for i in range(3):
    t.init(mode=Timer.ONE_SHOT,
            period=2000,
            callback=lambda x:print(x)
    )
    sleep_ms(1000)

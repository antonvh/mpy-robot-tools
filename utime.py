# Stub for testing purposes and ESP32 compatibility

import time

def ticks_ms():
    return int(time.time()*1000)

def ticks_diff(a,b):
    return a-b

def sleep_ms(duration):
    time.sleep(duration/1000)
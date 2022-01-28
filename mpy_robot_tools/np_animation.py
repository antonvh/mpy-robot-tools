# This library is handy for driving neopixel animations in a tight loop
# It works much like a mechanism, with time functions and keyframes.

from neopixel import NeoPixel
from machine import Pin
import utime
from math import sin, pi

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def saturate(value):
    return clamp(value, 0.0, 1.0)

def hue_to_rgb(h):
    r = abs(h * 6.0 - 3.0) - 1.0
    g = 2.0 - abs(h * 6.0 - 2.0)
    b = 2.0 - abs(h * 6.0 - 4.0)
    return saturate(r), saturate(g), saturate(b)

def hsl_to_rgb(h, s, l):
    # Takes hue in range 0-359, 
    # Saturation and lightness in range 0-99
    h /= 359
    s /= 100
    l /= 100
    r, g, b = hue_to_rgb(h)
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    r = (r - 0.5) * c + l
    g = (g - 0.5) * c + l
    b = (b - 0.5) * c + l
    rgb = tuple([round(x*255) for x in (r,g,b)])
    return rgb

def rgb_to_hsl(r, g, b):
    r = float(r/255)
    g = float(g/255)
    b = float(b/255)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, l = ((high + low) / 2,)*3

    if high == low:
        h = 0.0
        s = 0.0
    else:
        d = high - low
        s = d / (2 - high - low) if l > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return round(h*360), round(s*100), round(l*100)

def to_grb(rgb):
    return bytes((rgb[1],rgb[0],rgb[2]))

def from_grb(grb):
    return grb[1],grb[0],grb[2]

# Neopixel has GRB colors, not rgb !
ORANGE = b'\x66\xfc\x03'
OFF = b'\x00\x00\x00'
WHITE = b'\xff\xff\xff'
RED = b'\x00\xff\x00'
DARK_RED = b'\x00\x44\x00'
BLUE = b'\x00\x00\xff'

def indicators(on=ORANGE, off=OFF, interval=500, name="indicators"):
    def func(time, **kwargs):
        switch=True
        if name in kwargs:
            switch = kwargs[name]
        return on if (time % (interval*2) < interval) and switch else off
    return func

def indicators_right(on=ORANGE, off=OFF, interval=500):
    def func(time, turn=0, **kwargs):
        return on if (time % (interval*2) < interval) and turn > 0 else off
    return func

def brake_lights(drive=DARK_RED, brake=RED, reverse=WHITE):
    def func(time, speed=0, **kwargs):
        if speed < 0:
            return reverse
        elif speed > 0:
            return drive
        else:
            return brake
    return func

def switch(on=WHITE, off=OFF, name="switch"):
    def func(time, **kwargs):
        switch=True
        if name in kwargs:
            switch = kwargs[name]
        return on if switch else off
    return func

def delayed_switch(on=RED, off=OFF, delay=2000):
    def func(time, **kwargs):
        return on if time < delay else off
    return func

def hue_shift(period=1000, offset=0):
    def func(time, **kwargs):
        hsl = (
            (time % period)/period*360,
            100, # Full saturation
            50, # Half lightness
        )
        return to_grb(hsl_to_rgb(*hsl))
    return func

def rotate(l, n):
    return l[-n:] + l[:-n]

def knight_rider(period=2000, width=6):
    stepsize = int(255/(width-1))
    strip = [0]*width + list(range(0,256,stepsize))
    r_strip = strip[:]
    r_strip.reverse()
    def func(time, **kwargs):
        n = round((time % period)/period * width*2)
        result = [OFF]*width
        for i in range(width):
            result[i] = bytes((0,max(rotate(strip,n)[i], rotate(r_strip,-n)[i]),0))
        return result
    return func

def knight_rider_gen(period=2000, width=6):
    stepsize = int(255/(width-1))
    strip = [0]*width + list(range(0,256,stepsize))
    r_strip = strip[:]
    r_strip.reverse()
    n = 0
    while n<=2*width:
        result = [OFF]*width
        for i in range(width):
            result[i] = bytes((0,max(rotate(strip,n)[i], rotate(r_strip,-n)[i]),0))
        yield int(period/(2*width)*n), result
        n+=1

EMERGENCY_1 = [
    (0,     [RED]*3+[OFF]*3),
    (150,   [OFF]*6),
    (200,   [RED]*3+[OFF]*3),
    (350,   [OFF]*6),
    (400,   [RED]*3+[OFF]*3),
    (450,   [OFF]*6),
    (500,  [OFF]*3+[BLUE]*3),
    (650,  [OFF]*6),
    (700,  [OFF]*3+[BLUE]*3),
    (850,  [OFF]*6),
    (900,  [OFF]*3+[BLUE]*3),
    (1050,  [OFF]*6),
    (1100,  [OFF]*6)
]

def keyframes(frames):
    frames.reverse()
    period = frames[0][0]
    if period is 0: period = 1
    def func(time, **kwargs):
        result = [OFF]
        for frame_time, pixels in frames:
            if time%period >= frame_time:
                result = pixels
                break
        return result
    return func

def keyframes_dict(frames_dict, key="animation"):
    for k in frames_dict:
        frames_dict[k].reverse()
    def func(time, **kwargs):
        result = [OFF]
        if key in kwargs:
            anim_key = kwargs[key]
            if anim_key in frames_dict:
                frames = frames_dict[anim_key]
                period = frames[0][0]
                if period is 0: period = 1
                for frame_time, pixels in frames:
                    if time%period >= frame_time:
                        result = pixels
                        break
        return result
    return func


class NPAnimation():
    def __init__(self, light_funcs:dict, pin:int=24, n_leds:int=1):
        self.np = NeoPixel(Pin(pin), n_leds)
        # self.leds = bytearray(n_leds * 3) #BGR
        self.light_funcs = light_funcs
        self.start_time = utime.ticks_ms()

    def update_leds(self, time=None, **kwargs):
        if not time:
            time = utime.ticks_diff(utime.ticks_ms(), self.start_time)
        for led_positions, func in self.light_funcs:
            grb = func(time, **kwargs)
            if type(grb) == bytes:
                for pos in led_positions:
                    self.np.buf[pos*3:pos*3+3] = grb
            if type(grb) == list:
                i = 0
                for pos in led_positions:
                    self.np.buf[pos*3:pos*3+3] = grb[i]
                    i+=1
                    if i >= len(grb): i = 0
        self.np.write()
                    




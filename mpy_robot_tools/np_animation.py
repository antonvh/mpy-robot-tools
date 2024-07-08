# This library is handy for driving neopixel animations in a tight loop
# It works much like a mechanism, with time functions and keyframes.

from neopixel import NeoPixel
from machine import Pin
import utime
from math import pi, sin

def __clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def __scale(val, src, dst):
    ## Returns the given value scaled from the scale of src to the scale of dst.
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def __saturate(value):
    return __clamp(value, 0.0, 1.0)

def __hue_to_rgb(h):
    r = abs(h * 6.0 - 3.0) - 1.0
    g = 2.0 - abs(h * 6.0 - 2.0)
    b = 2.0 - abs(h * 6.0 - 4.0)
    return __saturate(r), __saturate(g), __saturate(b)

def hsl_to_rgb(h, s, l):
    """Turns h, s and l values into an rgb tuple

    Args:
        h (int/float): hue in range 0-359
        s (int/float): saturation in range 0-99
        l (int/float): lightness in range 0-99

    Returns:
        tuple: (r,g,b) in range 0-255
    """
    h /= 359
    s /= 100
    l /= 100
    r, g, b = __hue_to_rgb(h)
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    r = (r - 0.5) * c + l
    g = (g - 0.5) * c + l
    b = (b - 0.5) * c + l
    rgb = tuple([round(x*255) for x in (r,g,b)])
    return rgb

def rgb_to_hsl(r, g, b):
    """Converts the values r,g and b into a hsl tuple

    Args:
        r (int): red
        g (int): green
        b (int): blue

    Returns:
        tuple: (h,s,l) with h in range 0-359, s & l in range 0-100
    """
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
    """Convert an (r,g,b) tuple into grb bytes for neopixel buffer

    Args:
        rgb (tuple): (r,g,b)

    Returns:
        bytes: grb values
    """
    return bytes((rgb[1],rgb[0],rgb[2]))

def from_grb(grb):
    """Convert 3 bytes of grb into a an rgb tuple

    Args:
        grb (bytes): grb buffer bytes

    Returns:
        tuple: (r,g,b)
    """
    return grb[1],grb[0],grb[2]

class grb():
    """Enumerator for grb byte colors.
    """
    ORANGE = b'\x66\xfc\x03'
    BLACK = NONE = OFF = b'\x00\x00\x00'
    WHITE = b'\xff\xff\xff'
    RED = b'\x00\xff\x00'
    DARK_RED = b'\x00\x44\x00'
    BLUE = b'\x00\x00\xff'
    YELLOW = b'\xff\xff\x00' #(255,255,0),
    GREEN = b'\xff\x00\x00' # (0,255,0),
    CYAN = b'\xff\x00\xff' #: (0,255,255),
    VIOLET = b'\x7f\x7f\xff' #: (127,127,255),
    MAGENTA = b'\x00\xff\xff' #: (255,0,255),
    GRAY = b'\x7f\x7f\x7f' #: (127,127,127),

class rgb():
    """Enumerator for rgb tuples
    """
    ORANGE = from_grb(grb.ORANGE)
    BLACK = NONE = OFF = from_grb(grb.BLACK)
    WHITE = from_grb(grb.WHITE)
    RED = from_grb(grb.RED)
    DARK_RED = from_grb(grb.DARK_RED)
    BLUE = from_grb(grb.BLUE)
    YELLOW = from_grb(grb.YELLOW)
    GREEN = from_grb(grb.GREEN)
    CYAN = from_grb(grb.CYAN)
    VIOLET = from_grb(grb.VIOLET)
    MAGENTA = from_grb(grb.MAGENTA)
    GRAY = from_grb(grb.GRAY)


def indicators(on=grb.ORANGE, off=grb.OFF, interval=500, name="indicators"):
    """Animator function for indicator car lights. Returns a function that can be assigned
    to leds in in an animation loops.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        on (3 grb bytes, optional): grb byte color. Defaults to grb.ORANGE.
        off (3 grb bytes, optional): grb byte color. Defaults to grb.OFF.
        interval (int, optional): time on and of in ms. Defaults to 500.
        name (str, optional): Name for on/off switch. Defaults to "indicators".
    """
    def func(time, **kwargs):
        switch=True
        if name in kwargs:
            switch = kwargs[name]
        return on if (time % (interval*2) < interval) and switch else off
    return func

def indicators_right(on=grb.ORANGE, off=grb.OFF, interval=500):
    """Deprecated
    """
    def func(time, turn=0, **kwargs):
        return on if (time % (interval*2) < interval) and turn > 0 else off
    return func

def brake_lights(drive=grb.DARK_RED, brake=grb.RED, reverse=grb.WHITE):
    """Returns a function that returns 3 grb bytes, depending on the value of speed.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        drive (3 grb bytes, optional): Color of leds while speed > 0. Defaults to grb.DARK_RED.
        brake (3 grb bytes, optional): Color of leds while speed == 0. Defaults to grb.RED.
        reverse (3 grb bytes, optional): Color of leds while speed < 0. Defaults to grb.WHITE.
        
    Returns:
        function: func(speed) that returns the 3 grb bytes for brake lights
    """
    def func(time, speed=0, **kwargs):
        if speed < 0:
            return reverse
        elif speed > 0:
            return drive
        else:
            return brake
    return func

def switch(on=grb.WHITE, off=grb.OFF, name="switch"):
    """Generates a function that returns either of two grb byte colors, depending on a bolean switch.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        on (3 grb bytes, optional): Color when argument is True. Defaults to grb.WHITE.
        off (3 grb bytes, optional): Color when argument is False. Defaults to grb.OFF.
        name (str, optional): Name for the keyword argument of the returned function. Defaults to "switch".
        
    Returns:
        function: func(time, switch=True) that returns the 3 grb bytes depending on the value of 'switch'
            and accepts an unused time argument.
    """
    def func(time, **kwargs):
        switch=True
        if name in kwargs:
            switch = kwargs[name]
        return on if switch else off
    return func

def delayed_switch(on=grb.RED, off=grb.OFF, delay=2000):
    """Generates a function that returns either of two grb byte colors, depending on the expiry of a timer.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        on (3 grb bytes, optional): Color when timer is running. Defaults to grb.RED.
        off (3 grb bytes, optional): Color when timer has expired. Defaults to grb.OFF.
        delay (int, optional): Timer length in ms. Defaults to 2000.
        
    Returns:
        function: func(time) that returns the 3 grb bytes depending on the timer.
    """
    def func(time, **kwargs):
        return on if time < delay else off
    return func

def hue_shift(period=1000, offset=0):
    """Generates a function that returns an ever shifting grb byte color, depending on time and the period.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        period (int, optional): Period length in ms. Defaults to 1000.
        
    Returns:
        function: func(time) that returns the 3 grb bytes depending on the time and period.
    """
    def func(time, **kwargs):
        hsl = (
            (time % period)/period*360,
            100, # Full saturation
            50, # Half lightness
        )
        return to_grb(hsl_to_rgb(*hsl))
    return func

def pulse(color=grb.WHITE, period=5000, offset=0, min_pct=0, max_pct=100):
    """Generates a function that returns a pulsing grb byte color, depending on time and the period.
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        color (3 grb bytes, optional): Color when brightest. Defaults to grb.WHITE. 
        period (int, optional): Period length in ms. Defaults to 5000.
        offset (int, optional): Offset for phase calculation from period. Defaults to 0.
        min_pct (int, optional): Brightness percentage when darkest. Defaults to 0.
        max_pct (int, optional): Brightness percentage when brightest. Defaults to 100.
        
    Returns:
        function: func(time) that returns the 3 grb bytes depending on the time and period.
    """
    def func(time, **kwargs):
        # Make b vary between 0.0 and 1.0 within the period
        b = __scale(sin((time+offset) * 2 * pi / period), (-1,1), (min_pct/100, max_pct/100))
        return bytes([int(b*c) for c in color])
    return func

def rotate(l, n):
    return l[-n:] + l[:-n]

def knight_rider(period=2000, width=6, color=grb.RED):
    """Generates a function that returns 'width * 3' grb bytes of color, depending on time and the period.
    It makes a red led light up knight-rider radar style.
    
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        color (3 grb bytes, optional): Color when brightest. Defaults to grb.WHITE. 
        period (int, optional): Period length in ms. Defaults to 5000.
        min_pct (int, optional): Brightness percentage when darkest. Defaults to 0.
        max_pct (int, optional): Brightness percentage when brightest. Defaults to 100.
        
    Returns:
        function: func(time) that returns the 3 grb bytes depending on the time and period.
    """
    def b(n, center):
        # Brightness function, gauss-like with a max of 1 around center
        return 2**(-1.5/width*(n-center)**2)
    
    def func(time, **kwargs):
        # Bounce the center from left to right with a sine function
        center = 0.5*(sin(time * 2 * pi/period)+1)*width
        # Return brightness adjusted color for each led.
        return [bytes([int(b(n,center)*c) for c in color]) for n in range(width)]
    return func

def knight_rider_gen(period=2000, width=6):
    """Generator functions for knight rider radar

    Args:
        period (int, optional): _description_. Defaults to 2000.
        width (int, optional): _description_. Defaults to 6.

    Yields:
        bytes: width*3 bytes with grb color
    """
    stepsize = int(255/(width-1))
    strip = [0]*width + list(range(0,256,stepsize))
    r_strip = strip[:]
    r_strip.reverse()
    n = 0
    while n<=2*width:
        result = [grb.OFF]*width
        for i in range(width):
            result[i] = bytes((0,max(rotate(strip,n)[i], rotate(r_strip,-n)[i]),0))
        yield int(period/(2*width)*n), result
        n+=1

EMERGENCY_1 = [
    (0,     [grb.RED]*3+[grb.OFF]*3),
    (150,   [grb.OFF]*6),
    (200,   [grb.RED]*3+[grb.OFF]*3),
    (350,   [grb.OFF]*6),
    (400,   [grb.RED]*3+[grb.OFF]*3),
    (450,   [grb.OFF]*6),
    (500,  [grb.OFF]*3+[grb.BLUE]*3),
    (650,  [grb.OFF]*6),
    (700,  [grb.OFF]*3+[grb.BLUE]*3),
    (850,  [grb.OFF]*6),
    (900,  [grb.OFF]*3+[grb.BLUE]*3),
    (1050,  [grb.OFF]*6),
    (1100,  [grb.OFF]*6)
]

def keyframes(frames):
    """Generates a function that returns the grb bytes of a keyframe list, depending on time.
    It looks up the color of the actual keyframe in the list.
    
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        frames (3 grb bytes, optional): list of tuples with time-offset and the corresponding grb bytearray. 
        
    Returns:
        function: func(time) that returns the grb bytes depending on the time and period.
    """
    frames.reverse()
    period = frames[0][0]
    if period == 0: period = 1
    def func(time, **kwargs):
        result = [grb.OFF]
        for frame_time, pixels in frames:
            if time%period >= frame_time:
                result = pixels
                break
        return result
    return func

def keyframes_dict(frames_dict, name="animation"):
    """Generates a function that returns grb bytes of color, depending on time and the selected
    animation. 
    
    This function is for use in a function matrix for an NPAnimation() object.

    Args:
        frames_dict: Dictionary of keyframe lists, the argument for the keyframes functions
        name (str, optional): keyword argument to pass the dictionary key to in the gererated function

    Returns:
        function: func(time, keyframes=dict_key) that returns the 3 grb bytes depending on the time.
    """
    for k in frames_dict:
        frames_dict[k].reverse()
    def func(time, **kwargs):
        result = [grb.OFF]
        if name in kwargs:
            anim_key = kwargs[name]
            if anim_key in frames_dict:
                frames = frames_dict[anim_key]
                period = frames[0][0]
                if period == 0: period = 1
                for frame_time, pixels in frames:
                    if time%period >= frame_time:
                        result = pixels
                        break
        return result
    return func


class NPAnimation():
    """Animation class that animates leds with a matrix of led positions and attached functions.
    
    Example:
        Here's how to define a function matrix and the call update_leds()::
        
            funcs = [
                [ [0,1,2,3,4,5], hue_shift(period=5000) ], # Set leds 0-5 to shift hues.
                [ [13,14,16,17], switch(on=WHITE, off=OFF, name="headlights_switch") ], # Switch leds 13-17 on and off by passing a keyword argument "headlight_switch"
                [ [12,23], indicators(name="right_indicators") ], # indicators
                [ [15,20], indicators(name="left_indicators") ],
                [ [18,19,21,22], brake_lights()] # tail lights. They take a 'speed' keyword argument to light accordingly
            ]
            
            npa=NPAnimation(funcs)
            while True:
                npa.update_leds(right_indicators=True, speed=5)
    
    Args:
            light_funcs (_type_): Function matrix
            pin (int, optional): Neopixel chain data pin. Defaults to 24.
            n_leds (int, optional): Number of leds in the NeoPixel chain. Defaults to max led positions in funcs
    
    """
    def __init__(self, light_funcs, pin:int=24, n_leds:int=0):
        if n_leds == 0:
            n_leds = max([max(n[0]) for n in light_funcs]) + 1
        self.np = NeoPixel(Pin(pin), n_leds)
        self.light_funcs = light_funcs
        self.start_time = utime.ticks_ms()

    def leds_off(self):
        """Turns all leds off.
        """
        self.np.fill((0, 0, 0,))
        self.np.write()

    def update_leds(self, time=None, **kwargs):
        """Update leds, depending on current time

        Args:
            time (int, optional): Pass current time if you don't want to use the internal timer.
        """
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
                    




from hub import display, Image
import utime
from random import randrange
from math import sin, pi

_ = 0
O = 8
x = 6
B = 9

tens_px = {
    0 : [
        [_,_],
        [_,_],
        [_,_],
        [_,_],
        [_,_]
    ],
    1 : [
        [_,O],
        [O,O],
        [_,O],
        [_,O],
        [_,O]
    ],
    2 : [
        [O,O],
        [_,O],
        [O,O],
        [O,_],
        [O,O]
    ],
    3 : [
        [O,O],
        [_,O],
        [O,O],
        [_,O],
        [O,O]
    ],
    4 : [
        [O,_],
        [O,_],
        [O,O],
        [_,O],
        [_,O]
    ],
    5 : [
        [O,O],
        [O,_],
        [O,O],
        [_,O],
        [O,O]
    ],
    6 : [
        [O,_],
        [O,_],
        [O,O],
        [O,O],
        [O,O]
    ],
    7 : [
        [O,O],
        [_,O],
        [O,_],
        [O,_],
        [O,_]
    ],
    8 : [
        [O,O],
        [O,O],
        [x,x],
        [O,O],
        [O,O]
    ],
    9 : [
        [O,O],
        [O,O],
        [O,O],
        [_,O],
        [O,O]
    ],
}

units_px = {
    0 : [
        [B,B,B],
        [B,_,B],
        [B,_,B],
        [B,_,B],
        [B,B,B]
    ],
    1 : [
        [_,B,_],
        [B,B,_],
        [_,B,_],
        [_,B,_],
        [B,B,B]
    ],
    2 : [
        [B,B,B],
        [_,_,B],
        [B,B,B],
        [B,_,_],
        [B,B,B]
    ],
    3 : [
        [B,B,B],
        [_,_,B],
        [B,B,B],
        [_,_,B],
        [B,B,B]
    ],
    4 : [
        [B,_,B],
        [B,_,B],
        [B,B,B],
        [_,_,B],
        [_,_,B]
    ],
    5 : [
        [B,B,B],
        [B,_,_],
        [B,B,B],
        [_,_,B],
        [B,B,B]
    ],
    6 : [
        [B,B,B],
        [B,_,_],
        [B,B,B],
        [B,_,B],
        [B,B,B]
    ],
    7 : [
        [B,B,B],
        [_,_,B],
        [_,B,_],
        [_,B,_],
        [_,B,_]
    ],
    8 : [
        [B,B,B],
        [B,_,B],
        [B,B,B],
        [B,_,B],
        [B,B,B]
    ],
    9 : [
        [B,B,B],
        [B,_,B],
        [B,B,B],
        [_,_,B],
        [B,B,B]
    ],
}

def image_99(number):
    error_image = Image("00000:09090:00900:09090:00000")
    try:
        if not 0 <= number <= 99:
            # Return an error cross
            return error_image
    except:
        # Return an error cross
        return error_image

    number = int(number)
    units = number % 10
    tens = number // 10
    # Join matrices
    result_px = []
    for i in range(5):
        result_px += [tens_px[tens][i] + units_px[units][i]]

    # Convert to string with semicolons
    result_str = ":".join(["".join([str(n) for n in r]) for r in result_px])
    return Image(result_str)

def codelines():
    """
    Generator for Tars-style codelines, as seen in insterstellar
    usage:
        mycodelines = codelines()
        image_matrix = next(mycodelines)
    """
    display = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    yield display

    current_line = 0
    while True:
        while current_line < 5:
            # Type a line
            line_length = randrange(6)
            for column in range(line_length):
                display[current_line][column] = 6
                yield display

                display[current_line][column] = 9
                yield display

            # Blinking cursor
            if line_length < 5:
                for n in range(6):
                    display[current_line][line_length] = 9
                    yield display

                    display[current_line][line_length] = 0
                    yield display

            current_line += 1

        delete_a_line = 1
        while delete_a_line:
            display.pop(0)
            display += [[0,0,0,0,0]]
            if current_line > 0: current_line -= 1
            yield display
            delete_a_line = randrange(2)

class LMAnimation():
    """
    Class for showing animations in your python script
    frames: can be a generator or list of 5x5 matrices.
    Frames can even be tuples of a frame duration and a 5x5 matrix.
    usage:
        animation = LMAnimation(my_frame_list)

        while True:
            animation.update_display()

    Note that the hub can also animate using the code below
    It wil not be synchronized to a timer, but you won't have to update it

    from hub import display, Image
    IMG_1 = Image("00000:09000:09000:09000:00000")
    IMG_2 = Image("00000:00900:00900:00900:00000")
    IMG_3 = Image("00000:00090:00090:00090:00000")
    ANIMATION = [IMG_1, IMG_2, IMG_3]
    display.show(ANIMATION, delay=100, wait=False, loop=True)
    """
    def __init__(self, frames, fps=12):
        self.frames = frames
        self.interval = int(1000/fps)
        self.start_time = utime.ticks_ms()
        self.next_frame_time = 0
        self.current_frame = 0

    def update_display(self, time=None):
        if not time:
            time = utime.ticks_diff(utime.ticks_ms(), self.start_time)
        if time >= self.next_frame_time:
            image = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
            
            if '__next__' in dir(self.frames):
                image = next(self.frames)
                self.next_frame_time += self.interval
            else:
                if len(self.frames[0]) > 2:
                    image = self.frames[self.current_frame]
                    self.next_frame_time += self.interval
                else:
                    image = self.frames[self.current_frame][1]
                    self.next_frame_time += self.frames[self.current_frame][0]
                self.current_frame += 1
                if self.current_frame >= len(self.frames):
                    self.current_frame = 0

            display.show(Image(":".join(["".join([str(n) for n in r]) for r in image])))

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

def to_bgr(rgb):
    return bytes((rgb[2],rgb[1],rgb[0]))

def from_bgr(bgr):
    return bgr[2],bgr[1],bgr[0]

ORANGE = b'\x00\xff\xff'
OFF = b'\x00\x00\x00'
WHITE = b'\xff\xff\xff'
RED = b'\x00\x00\xff'
BLUE = b'\xff\x00\x00'

def indicators(on=ORANGE, off=OFF, interval=500):
    def func(time, **kwargs):
        return on if time % (interval*2) < interval else off
    return func

def switch(on=WHITE, off=OFF):
    def func(time, switch=True):
        return on if switch else off
    return func

def delayed_switch(on=RED, off=OFF, delay=2000):
    def func(time):
        return on if time < delay else off
    return func

def hue_wave(a=BLUE, b=RED, period=1000, offset=0):
    ha, sa, la = rgb_to_hsl(from_bgr(a))
    hb, sb, lb = rgb_to_hsl(from_bgr(b))
    hd, sd, ld = abs(hb-ha), abs(sb-sa), abs(lb-la)
    hbase, sbase, lbase = min((ha,hb)), min((sa,sb)), min((la,lb))
    def func(time):
        # range between 0.0 and 1.0 depending on time and period
        gradient = (sin((x-offset)/period*2*pi)+1)/2
        hsl = (
            hbase + hd * gradient,
            sbase + sd * gradient,
            lbase + ld * gradient,
        )
        return to_bgr(hsl_to_rgb(hsl))
    return func

class LedAnimation():
    def __init__(self, n_leds:int, light_funcs:dict):
        self.leds = bytearray(n_leds * 3) #BGR
        self.light_funcs = light_funcs
        # self.interval = int(1000/fps)
        self.start_time = utime.ticks_ms()

    def update_leds(self, time=None, **kwargs):
        if not time:
            time = utime.ticks_diff(utime.ticks_ms(), self.start_time)
        for led_positions, func in self.light_funcs.items():
            bgr = func(time, **kwargs)
            for pos in led_positions:
                self.leds[pos*3:pos*3+3] = bgr

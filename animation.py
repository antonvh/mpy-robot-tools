from random import randrange
import utime
import hub

# ASCII art lightness
B = 9
W = 8
O = 7
o = 6
x = 5
z = 4
l = 3
_ = 0


frames = [
    [
        [B,B,_,B,B],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]],
    [
        [B,B,_,_,_],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]],
]

timed_frames = [
    (1000, 
    [
        [B,B,_,B,B],
        [B,B,_,B,B],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]
    ]),
    (300,
    [
        [B,B,_,_,_],
        [B,B,_,o,o],
        [_,_,_,_,_],
        [B,_,_,_,B],
        [_,B,B,B,_]
    ]),
]

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

class AMHAnimation():
    """
    Class for showing animations in your python script
    frames: can be a generator or list of 5x5 matrices.
    Frames can even be tuples of a frame duration and a 5x5 matrix.
    usage:
        animation = AMHAnimation(my_frame_list)

        while True:
            animation.update_display()
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

            hub.display.show(hub.Image(":".join(["".join([str(n) for n in r]) for r in image])))
            


codelines_frames = codelines()
animation = AMHAnimation(codelines_frames)

while True:
    animation.update_display()

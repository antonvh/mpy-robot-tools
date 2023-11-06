from projects.mpy_robot_tools.bt import MidiController, CHORD_STYLES, note_parser
from mindstorms import ColorSensor
from time import sleep_ms
from projects.mpy_robot_tools.pybricks import UltrasonicSensor
from hub import port

mc = MidiController()
cs = ColorSensor('D')

def strum_chord(base, chord_style="M", duration=1000, delay=21):
    """
    Turn chords notes on from low to high, with a slight delay,
    just as if you're strumming strings on a guitar.
    """
    note = note_parser(base)
    for interval in CHORD_STYLES[chord_style]:
        mc.note_on(note + interval, 120)
        sleep_ms(delay)
    # sleep_ms(duration-200)
    # mc.chord_off(base, style=chord_style)

while 1:
    if cs.get_reflected_light() > 50:
        strum_chord("C4")
    else:
        mc.chord_off("C4")
# Run this program on Daniele Benedetelli's guitor model, from within the mindstorms software.
# Install mpy_robot_tools first. https://github.com/antonvh/mpy-robot-tools/blob/master/Installer/install_mpy_robot_tools.py

from projects.mpy_robot_tools.bt import MidiController, CHORD_STYLES, note_parser
from mindstorms import ColorSensor, DistanceSensor
from time import sleep_ms, ticks_ms
from hub import port

mc = MidiController()
cs = ColorSensor('D')
ds = DistanceSensor('C')

def strum_chord(base, chord_style="M", duration=1000, delay=30):
    """
    Turn chords notes on from low to high, with a slight delay,
    just as if you're strumming strings on a guitar.
    """
    note = note_parser(base)
    for interval in CHORD_STYLES[chord_style]:
        mc.note_on(note + interval, 120)
        sleep_ms(delay)

while 1:
    if cs.get_reflected_light() > 50:
        note = 60 - round((ds.get_distance_cm() - 8)/42 * 11)
        strum_chord(note,"M")
        while cs.get_reflected_light() > 50:
            pass
        mc.chord_off(note, 0, style="M")
        



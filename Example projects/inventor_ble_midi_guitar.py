# Run this program on Daniele Benedetelli's guitor model, from within the mindstorms software.
# Get the book here: https://nostarch.com/lego-mindstorms-robot-inventor-activity-book
# Install mpy_robot_tools first. https://github.com/antonvh/mpy-robot-tools/blob/master/Installer/install_mpy_robot_tools.py

from projects.mpy_robot_tools.bt import MidiController, CHORD_STYLES
from mindstorms import ColorSensor, DistanceSensor, Motor, MSHub

# Devices
mshub = MSHub()
mc = MidiController()
cs = ColorSensor('D')
ds = DistanceSensor('C')
mf = Motor('F')
mb = Motor('B')

# Constants
C3 = 48 # Midi note number for C in the third octave
STYLE_KEYS = list(CHORD_STYLES.keys()) # Dictionary keys, not piano keys.
print(STYLE_KEYS)
MAX_IDX = len(STYLE_KEYS)-1
KEYS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"] # Harmonic keys

# Reset degrees counted to abs position
mb.set_degrees_counted(
    (mb.get_position()+180) % 360 - 180
    )

# Initialize values
ds.light_up_all()
mode = "C" # chromatic or "D" for diatonic
chord_style="P"
setting_dial = last_setting_dial = 0
key = 0
note = last_note = C3
notes = [note+chord_offset for chord_offset in CHORD_STYLES[chord_style]]

def diatonic_chord(note, key):
    abs_key = C3+key
    offset = note - abs_key
    chord_style = "m"
    if offset in [1, -2, -4, -6, -9, -11, -13]:
        # Quantize half tone down for notes not in the diatonic scale
        offset -= 1

    # Set chord style according to note in scale
    if offset == -5:
        chord_style = "7"
    elif offset == -1:
        chord_style = "dim7"
    elif offset in [0, -7, -12 ]:
        chord_style = "M"

    # Put everything together in a list comprehension and return
    return [ abs_key+offset+chord_offset for chord_offset in CHORD_STYLES[chord_style] ]

while 1:
    setting_dial = mb.get_degrees_counted() // 45
    # End of the neck is 52cm, beginning 4cm. 
    note = C3+key - int((ds.get_distance_cm() or 0) / 3.1) + 7

    if note != last_note:
        last_note = note
        # print(note)
        if mode == "D":
            # Diatonic. Quantize chord to diatonic scale.
            notes = diatonic_chord(note, key)
        elif mode == "C":
            notes = [ note+chord_offset for chord_offset in CHORD_STYLES[chord_style] ]

    if 90 > mf.get_position() > 15:
        mc.note_on(notes[0], 120)
        while mf.get_position() < 25:
            pass
        mc.note_on(notes[1], 120)
        while mf.get_position() < 35:
            pass
        mc.note_on(notes[2], 120)
        while mf.get_position() < 45:
            pass
        mc.note_on(notes[3], 120)

        while 100 > mf.get_position() > 15:
            pass
        mc.write_midi_notes(notes, on=False)
    
    elif last_setting_dial != setting_dial:
        last_setting_dial = setting_dial
        if mode == "C":
            key=0
            chord_style = STYLE_KEYS[min(max(setting_dial, 0), MAX_IDX)]
            # This is a blocking call, so only do it on change.
            mshub.light_matrix.write(chord_style)
        if mode == "D":
            key = min(max(setting_dial, 0), 11)
            mshub.light_matrix.write(KEYS[key])

    elif mshub.left_button.is_pressed():
        while mshub.left_button.is_pressed():
            pass
        mode = "C"
        mshub.light_matrix.write(mode)

    elif mshub.right_button.is_pressed():
        while mshub.right_button.is_pressed():
            pass
        mode = "D"
        mshub.light_matrix.write(mode)
        



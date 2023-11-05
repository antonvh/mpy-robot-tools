from bt import MidiController, CHORD_STYLES, note_parser
from time import sleep_ms

mc = MidiController()

STRUM = True

# Chords from "The Lion Sleeps Tonight". All are Major (M)
chords_basenotes = ["C3", "C3", "F2", "F2", "C3", "C3", "G2", "G2", ]

def strum_chord(base, chord_style="M", duration=1000, delay=25):
    """
    Turn chords notes on from low to high, with a slight delay,
    just as if you're strumming strings on a guitar.
    """
    note = note_parser(base)
    for interval in CHORD_STYLES[chord_style]:
        mc.note_on(note + interval, 120)
        sleep_ms(delay)
    sleep_ms(duration-200)
    mc.chord_off(base, style=chord_style)


while 1:
    for basenote in chords_basenotes:
        if STRUM:
            strum_chord(basenote)
        else:
            mc.play_chord(basenote)

    
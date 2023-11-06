import ubluetooth
from time import ticks_ms, sleep_ms
from . import BLEHandler, advertising_payload, _FLAG_NOTIFY, _FLAG_READ, _FLAG_WRITE_NO_RESPONSE

# MIDI
MIDI_SERVICE_UUID = ubluetooth.UUID("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
MIDI_CHAR_UUID = ubluetooth.UUID("7772E5DB-3868-4112-A1A9-F2669D106BF3")
MIDI_CHAR = (
    MIDI_CHAR_UUID,
    _FLAG_NOTIFY | _FLAG_READ | _FLAG_WRITE_NO_RESPONSE, 
)
MIDI_SERVICE = (
    MIDI_SERVICE_UUID,
    (MIDI_CHAR,),
)

# MIDI Note conversion and scales
# From C3 - A and B are above G
# Semitones     A   B   C   D   E   F   G
NOTE_OFFSET = [21, 23, 12, 14, 16, 17, 19]

#: Chord styles for the play_chord method of the MidiController class.
CHORD_STYLES = { 
    # Note (half tone) offsets from base note
    "M": (0, 4, 7, 12), 
    "m": (0, 3, 7, 12), 
    "7": (0, 4, 7, 10),
    "m7": (0, 3, 7, 10),
    "M7": (0, 4, 7, 11),
    "sus4": (0, 5, 7, 12),
    "sus2": (0, 2, 7, 12),
    "dim7": (0, 3, 6, 10),
    "P": (0,7,12,19), # Power chord
    }

def note_parser(note):
    # Note parser from "https://github.com/adafruit/Adafruit_CircuitPython_MIDI.git"
    """If note is a string then it will be parsed and converted to a MIDI note (key) number, e.g.
    "C4" will return 60, "C#4" will return 61. If note is not a string it will simply be returned.

    :param note: Either 0-127 int or a str representing the note, e.g. "C#4"
    """
    midi_note = note
    if isinstance(note, str):
        if len(note) < 2:
            raise ValueError("Bad note format")
        noteidx = ord(note[0].upper()) - 65  # 65 os ord('A')
        if not 0 <= noteidx <= 6:
            raise ValueError("Bad note")
        sharpen = 0
        if note[1] == "#":
            sharpen = 1
        elif note[1] == "b":
            sharpen = -1
        midi_note = int(note[1 + abs(sharpen) :]) * 12 + NOTE_OFFSET[noteidx] + sharpen
    return midi_note


class MidiController:
    """
    Class for a MIDI BLE Controller. Turn your MINDSTORMS hub or LMS-ESP32 into a MIDI musical instrument!

    :param name: The name of the MIDI controller
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    """
    def __init__(self, name="amh-midi", ble_handler=None):
        if ble_handler is None:
            self.ble_handler = BLEHandler()
        else:
            self.ble_handler = ble_handler
        ((self.handle_midi,),) = self.ble_handler._ble.gatts_register_services((MIDI_SERVICE,))
        self.ble_handler.advertise(advertising_payload(name=name[:8], services=[MIDI_SERVICE_UUID]))

    def write_midi_msg(self, cmd, data0, data1):
        """
        Timestamps and writes a MIDI message to the BLE GATT server.
        See https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message for MIDI message format.

        :param cmd: MIDI command byte
        :type cmd: byte or int
        :param data0: MIDI data byte 0
        :type data0: byte or int
        :param data1: MIDI data byte 1
        :type data1: byte or int
        """
        d = bytearray(5)
        timestamp_ms = ticks_ms()
        d[0] = (timestamp_ms >> 7 & 0x3F) | 0x80
        d[1] = 0x80 | (timestamp_ms & 0x7F)
        d[2] = cmd
        d[3] = data0
        d[4] = data1
        self.ble_handler.notify(d, self.handle_midi)
    
    def write_midi_chord(self, cmd, data0, data1, style="M"):
        """
        Timestamps and writes a MIDI chord to the BLE GATT server.

        :param cmd: MIDI command byte (0x90 for note on, 0x80 for note off)
        :type cmd: byte or int
        :param data0: MIDI data byte 0 (note number)
        :type data0: byte or int
        :param data1: MIDI data byte 1 (velocity)
        :type data1: byte or int
        :param style: Chord style. See CHORD_STYLES for possible values.
        :type style: str
        """
        d = bytearray(11)
        timestamp_ms = ticks_ms()
        d[0] = (timestamp_ms >> 7 & 0x3F) | 0x80
        d[1] = 0x80 | (timestamp_ms & 0x7F)
        d[2] = cmd
        d[3] = data0 + CHORD_STYLES[style][0]
        d[4] = data1
        d[5] = data0 + CHORD_STYLES[style][1]
        d[6] = data1
        d[7] = data0 + CHORD_STYLES[style][2]
        d[8] = data1
        d[9] = data0 + CHORD_STYLES[style][3]
        d[10] = data1
        self.ble_handler.notify(d, self.handle_midi)

    def note_on(self, note, velocity):
        """
        Send a MIDI 'note on' message.

        :param note: The note to play. Can be a MIDI note number (0-127) or a string like "C4" or "C#4"
        :type note: byte or int or str
        :param velocity: The velocity of the note key press (0-127)
        :type velocity: byte or int
        """
        self.write_midi_msg(0x90, note_parser(note), velocity )

    def note_off(self, note, velocity=0):
        """
        Send a MIDI 'note off' message.

        :param note: The note to stop playing. Can be a MIDI note number (0-127) or a string like "C4" or "C#4"
        :type note: byte or int or str
        :param velocity: The velocity of the note key release (0-127)
        :type velocity: byte or int
        """
        self.write_midi_msg(0x80, note_parser(note), velocity )
        
    def control_change(self, control, value):
        """
        Send a MIDI CC 'control change' message. Handy for your ableton live controller.

        :param control: The control number (0-127)
        :type control: byte or int
        :param value: The value of the control (0-127)
        :type value: byte or int
        """
        self.write_midi_msg(0xB0, control, value)
        
    def chord_on(self, base, velocity, style="M"):
        """
        Start playing a MIDI chord.

        :param base: The base note of the chord. Can be a MIDI note number (0-127) or a string like "C4" or "C#4"
        :type base: byte or int or str
        :param velocity: The velocity of the chord key press (0-127)
        :type velocity: byte or int
        :param style: Chord style. See CHORD_STYLES for possible values.
        """
        self.write_midi_chord(0x90, note_parser(base), velocity, style)

    def chord_off(self, base, velocity=0, style="M"):
        """
        Stop playing a MIDI chord.
        """
        self.write_midi_chord(0x80, note_parser(base), velocity, style)

    def play_chord(self, base, style="M", duration=1000):
        """
        Play a MIDI chord for a given duration.

        :param base: The base note of the chord. Can be a MIDI note number (0-127) or a string like "C4" or "C#4"
        :type base: byte or int or str
        :param style: Chord style. See CHORD_STYLES for possible values.
        :param duration: The duration of the chord in milliseconds
        :type duration: int

        """
        self.chord_on(base, 100, style)
        sleep_ms(duration*7//10)
        self.chord_off(base, 100, style)
        sleep_ms(duration*3//10)
BUTTONS = 0
controller_state=[0]

def set_button(num, pressed):
    if 0 < num < 9:
        bitmask = 0b1 << (num-1)
        if pressed:
            controller_state[BUTTONS] |= bitmask
        else:
            controller_state[BUTTONS] &= ~bitmask

def test_set_button():
    set_button(1, True)
    assert controller_state[BUTTONS] is 0b1
    set_button(2, True)
    assert controller_state[BUTTONS] is 0b11
    set_button(3, True)
    assert controller_state[BUTTONS] is 0b111
    set_button(2, False)
    assert controller_state[BUTTONS] is 0b101
    set_button(5, True)
    assert controller_state[BUTTONS] is 0b10101
    set_button(2, False)
    assert controller_state[BUTTONS] is 0b10101

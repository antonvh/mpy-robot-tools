import hub

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
    error_image = hub.Image("00000:09090:00900:09090:00000")
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
    return hub.Image(result_str)

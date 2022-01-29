class NeoPixel():
    def __init__(self, pin, n_pixels) -> None:
        self.buf = bytearray(n_pixels*3)
        self.pin = pin
        self.n_pixels = n_pixels

    def write(self):
        pass

    def fill(self, color):
        grb=color[1],color[0],color[2]
        self.buf = bytearray(grb*self.n_pixels)
# Stub for testing purposes and ESP32 compatibility
# With this you can go:
# from hub_stub import port
# port.A.motor.get()
# >>> []

def Image(s):
    return(s)

class Display():
    def show(self, s, **kwargs):
        return s

display = Display()

class Motor():
    @staticmethod
    def get():
        return []
    def dc():
        pass

class Device(Motor):
    motor = Motor()

class port():
    A = Device()
    B = Device()
    C = Device()
    D = Device()
    E = Device()
    F = Device()

class sound():
    @staticmethod
    def beep(*args):
        pass
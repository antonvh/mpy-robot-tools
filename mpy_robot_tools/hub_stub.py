# Stub for testing purposes and ESP32 compatibility
# With this you can go:
# from hub_stub import port
# port.A.motor.get()
# >>> []

def Image(s):
    return(s)

def display():
    pass

display.show = lambda x: print(x)

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

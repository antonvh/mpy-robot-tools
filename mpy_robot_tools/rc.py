# Testing imports

from .bt import UARTPeripheral

class MyRCClass(UARTPeripheral):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

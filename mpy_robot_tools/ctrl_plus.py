import struct
try:
    from micropython import const
    from time import sleep_ms
except:
    def const(x):
        return x
    def sleep_ms(x):
        pass
try:
    from .bt import BLEHandler
except:
    from bt import BLEHandler

__HUB_NOTIFY_DESC = const(0x0F)
__REMOTE_NOTIFY_DESC = const(0x0C)
__MARIO_NOTIFY_DESC = const(14)
__HUB_PORT_ACC = const(0x61)
__HUB_PORT_GYRO = const(0x62)
__HUB_PORT_TILT = const(0x63)

_MODE = const(0)
_MODE_BYTE = const(1)
_MODE_DATA_SETS = const(2)
_MODE_DATA_SET_TYPE = const(3)

OFF = const(0)
PINK = const(1)
PURPLE = const(2)
DARK_BLUE = const(3)
BLUE = const(4)
TEAL = const(5)
GREEN = const(6)
YELLOW = const(7)
ORANGE = const(8)
RED = const(9)
WHITE = const(10)

def clamp_int(n, floor=-100, ceiling=100):
    return max(min(round(n), ceiling), floor)

class SmartHub():
    __PORTS = {
        1:0, 2:1, 3:2, 4:3,
        "A":0, "B":1, "C":2, "D":3}

    def __init__(self, ble_handler:BLEHandler=None):
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler
        self._conn_handle = None
        self.acc_sub = False
        self.gyro_sub = False
        self.tilt_sub = False
        self.hub_data = {}
        self.mode_info = {}

    def is_connected(self):
        return self._conn_handle is not None

    def connect(self):
        self._conn_handle = self.ble_handler.connect_lego()
        if self._conn_handle is not None:
            sleep_ms(500)
            # Subscribe to motion data of SMART Hubs
            self.write(0x0A, 0x00, 0x41, __HUB_PORT_ACC, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)
            self.write(0x0A, 0x00, 0x41, __HUB_PORT_GYRO, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)
            self.write(0x0A, 0x00, 0x41, __HUB_PORT_TILT, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)

            # Initialize all ports with mode 0
            mode = 0
            for i in range(4):
                # SUBSCRIBE_MODE
                self.write(0x0A,0x00,0x41, i, mode, 0x01, 0x00, 0x00, 0x00, 0x01)
                sleep_ms(100)
                # GET_MODE_INFO
                self.write(0x06, 0x00, 0x22, i, mode, 0x80)
                sleep_ms(100)

            # Enable notify on smart hubs
            self.ble_handler.enable_notify(self._conn_handle, __HUB_NOTIFY_DESC, self.__on_notify)
            sleep_ms(200)
            self.set_led_color(GREEN)
        else:
            print("Connection failed")

    def disconnect(self):
        if self._conn_handle is not None:
            self.ble_handler.disconnect(self._conn_handle)
            self._conn_handle = None

    def write(self, *data):
        self.ble_handler.lego_write(
            struct.pack("%sB" % len(data), *data),
            self._conn_handle
            )

    def set_led_color(self, idx):
        self.write(0x08, 0x00, 0x81, 0x32, 0x11, 0x51, 0x00, idx)

    def set_remote_led_color(self, idx):
        self.write(0x08, 0x00, 0x81, 0x34, 0x11, 0x51, 0x00, idx)

    def __on_notify(self, data):
        # hub = data[1]
        message_type = data[2]
        port = data[3]
        payload = data[4:]
        if message_type == 0x45:
            self.hub_data[port] = payload
        elif message_type == 0x44:
            self.mode_info[port] = {
                _MODE : payload[0],
                _MODE_BYTE : payload[1],
                _MODE_DATA_SETS : payload[2],
                _MODE_DATA_SET_TYPE : payload[3],
            }

    def unpack_data(self, port, fmt="3h"):
        if port in self.hub_data.keys():
            return struct.unpack(fmt, self.hub_data[port])

    def acc(self):
        return self.unpack_data(__HUB_PORT_ACC)

    def gyro(self):
        return self.unpack_data(__HUB_PORT_GYRO)

    def tilt(self):
        return self.unpack_data(__HUB_PORT_TILT)

    def dc(self, port, pct):
        self.write(0x06, 0x00, 0x81, self.__PORTS[port], 0x11, 0x51, 0x00, clamp_int(pct))

    def run_target(self, port, degrees, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        degree_bits = struct.unpack("<BBBB", struct.pack("<i", degrees))
        self.write(0x0D, 0x00, 0x81, self.__PORTS[port], 0x11, 0x0D, degree_bits[0], degree_bits[1], degree_bits[2], degree_bits[3], speed, max_power, 0x7E)

    def mode(self, port, mode, *data):
        # set_mode
        self.write(0x0A,0x00,0x41, self.__PORTS[port], mode, 0x01, 0x00, 0x00, 0x00, 0x01)
        sleep_ms(100)
        if data:
            self.write(7+len(data), 0x00, 0x81, self.__PORTS[port], 0x00, 0x51, mode, *data)
            sleep_ms(100)
        # request_mode_info
        self.write(0x06, 0x00, 0x22, self.__PORTS[port], mode, 0x80)
        sleep_ms(100)

    def run(self, port, speed, max_power=100, acceleration=100, deceleration=100):
        # Start motor at given speed
        self.write(0x09, 0x00, 0x81, self.__PORTS[port], 0x11, 0x07, clamp_int(speed), max_power, 0x00)

    def run_time(self, port, time, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        # Rotate motor for a given time
        time_bits = struct.unpack("<BB", struct.pack("<H", time))
        self.write(0x0B, 0x00, 0x81, self.__PORTS[port], 0x11, 0x09, time_bits[0], time_bits[1], speed, max_power, 0x00)

    def run_angle(self, port, degrees, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        # Rotate motor for a given number of degrees relative to current position
        degree_bits = struct.unpack("<BBBB", struct.pack("<i", degrees))
        self.write(0x0D, 0x00, 0x81, self.__PORTS[port], 0x11, 0x0B, degree_bits[0], degree_bits[1], degree_bits[2], degree_bits[3], speed, max_power, 0x7E)

    def get(self, port):
        port = self.__PORTS[port]
        if port in self.hub_data:
            value = None
            payload = self.hub_data[port]
            no_data_sets = None
            data_set_type = 0
            if port in self.mode_info:
                data_set_type = self.mode_info[port][_MODE_DATA_SET_TYPE]
                no_data_sets = self.mode_info[port][_MODE_DATA_SETS]

            if data_set_type == 0x00:
                message = struct.unpack("%sb" % len(payload), payload)
                value = message[:no_data_sets]
            elif data_set_type == 0x01:
                message = struct.unpack("%sh" % (len(payload)//2), payload)
                value = message[:no_data_sets]
            elif data_set_type == 0x02:
                message = struct.unpack("%si" % (len(payload)//4), payload)
                value = message[:no_data_sets]
            return value
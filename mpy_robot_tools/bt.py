from hub import display, Image
import bluetooth
import struct
from time import sleep_ms
from micropython import const, schedule
from machine import Timer

_CONNECT_IMAGES= [
    Image('03579:00000:00000:00000:00000'),
    Image('00357:00000:00000:00000:00000'),
    Image('00035:00000:00000:00000:00000'),
    Image('00003:00000:00000:00000:00000'),
    Image('00000:00000:00000:00000:00009'),
    Image('00000:00000:00000:00000:00097'),
    Image('00000:00000:00000:00000:00975'),
    Image('00000:00000:00000:00000:09753'),
    Image('00000:00000:00000:00000:97530'),
    Image('00000:00000:00000:00000:75300'),
    Image('00000:00000:00000:00000:53000'),
    Image('90000:00000:00000:00000:30000'),
    Image('79000:00000:00000:00000:00000'),
    Image('57900:00000:00000:00000:00000'),
    Image('35790:00000:00000:00000:00000'),
]

L_STICK_HOR = const(0)
L_STICK_VER = const(1)
R_STICK_HOR = const(2)
R_STICK_VER = const(3)
L_TRIGGER = const(4)
R_TRIGGER = const(5)
SETTING1 = const(6)
SETTING2 = const(7)
BUTTONS = const(8)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

_NOTIFY_ENABLE = const(1)
_INDICATE_ENABLE = const(2)

if 'FLAG_INDICATE' in dir(bluetooth):
    # We're on MINDSTORMS Robot Inventor
    # New version of bluetooth
    _IRQ_GATTS_WRITE = 3
    _IRQ_SCAN_RESULT = 5
    _IRQ_SCAN_DONE = 6
    _IRQ_PERIPHERAL_CONNECT = 7
    _IRQ_PERIPHERAL_DISCONNECT = 8
    _IRQ_GATTC_SERVICE_RESULT = 9
    _IRQ_GATTC_CHARACTERISTIC_RESULT = 11
    _IRQ_GATTC_READ_RESULT = 15
    _IRQ_GATTC_NOTIFY = 18
    _IRQ_GATTC_CHARACTERISTIC_DONE = 12
    _IRQ_GATTC_SERVICE_DONE = 10
    _IRQ_GATTC_WRITE_DONE = 17
else:
    # We're probably on SPIKE Prime
    _IRQ_GATTS_WRITE = 1<<2
    _IRQ_SCAN_RESULT = 1 << 4
    _IRQ_SCAN_DONE = 1 << 5
    _IRQ_PERIPHERAL_CONNECT = 1 << 6
    _IRQ_PERIPHERAL_DISCONNECT = 1 << 7
    _IRQ_GATTC_SERVICE_RESULT = 1 << 8
    _IRQ_GATTC_CHARACTERISTIC_RESULT = 1 << 9
    _IRQ_GATTC_READ_RESULT = 1 << 11
    _IRQ_GATTC_NOTIFY = 1 << 13
    _IRQ_GATTC_CHARACTERISTIC_DONE = 1 << 12
    _IRQ_GATTC_SERVICE_DONE = 1 << 9
    _IRQ_GATTC_WRITE_DONE = 1 << 16

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Helpers for generating BLE advertising payloads.
# Advertising payloads are repeated packets of the following form:
#1 byte data length (N + 1)
#1 byte type (see constants below)
#N bytes type-specific data

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
# _ADV_TYPE_UUID16_MORE = const(0x2)
# _ADV_TYPE_UUID32_MORE = const(0x4)
# _ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)


_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_LEGO_SERVICE_UUID = bluetooth.UUID("00001623-1212-EFDE-1623-785FEABCD123")
_LEGO_SERVICE_CHAR = bluetooth.UUID("00001624-1212-EFDE-1623-785FEABCD123")
_UART_TX = (
    _UART_TX_UUID,
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    _UART_RX_UUID,
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

def clamp_int(n, floor=-100, ceiling=100):
    return max(min(int(n),ceiling),floor)

# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload


def decode_field(payload, adv_type):
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2 : i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def decode_name(payload):
    n = decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], "utf-8") if n else ""


def decode_services(payload):
    services = []
    for u in decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<h", u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<d", u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(bluetooth.UUID(u))
    return services

class BLEHandler():
    # Basic BT class that can be a central or peripheral or both
    # The central always connects to a peripheral. The Peripheral just advertises.
    def __init__(self, debug=False):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()
        self.debug = debug

    def _reset(self):
        self._connected_centrals = set()
        self._scan_result_callback = None
        self._scan_done_callback = None
        self._conn_callback = None
        self._disconn_callback = None
        self._central_conn_callback = None # Used when centrals connect
        self._central_disconn_callback = None # Used when centrals disconnect
        self._char_result_callback = None
        self._read_callback = None
        self._write_callbacks = {}
        self._notify_callbacks = {}
        self._search_name = None
        self.connecting_uart = False
        self.connecting_lego = False
        self._read_data = []
        self._reading=False
        self._start_handle = None
        self._end_handle = None

    def info(self, *messages):
        if self.debug:
            print(*messages)

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            name=decode_name(adv_data) or "?"
            services=decode_services(adv_data)
            self.info("Found: ",name , "with services:", services)
            if self.connecting_uart:
                # Move this back to base class
                if name == self._search_name and _UART_UUID in services: #Allow for nameless scanning too? Search by services?
                    # Found a potential device, remember it
                    self._addr_type = addr_type
                    self._addr = bytes(addr) # Note: addr buffer is owned by caller so need to copy it.
                    # ... and stop scanning. This triggers the IRQ_SCAN_DONE and the on_scan callback.
                    self.stop_scan()
            if self.connecting_lego:
                if _LEGO_SERVICE_UUID in services:
                    self._addr_type = addr_type
                    self._addr = bytes(addr)
                    self._adv_type = adv_type
                    self._name = decode_name(adv_data)
                    self._services = decode_services(adv_data)
                    # self._man_data = decode_manufacturer(adv_data)
                    self.stop_scan()
            if self._scan_result_callback:
                self._scan_result_callback(addr_type, addr, name, services)

        elif event == _IRQ_SCAN_DONE:
            if self.connecting_uart:
                if self._addr_type is not None:
                    print("Found peripheral:", self._search_name)
                    sleep_ms(500)
                    self._ble.gap_connect(self._addr_type, self._addr)
                else:
                    self.connecting_uart = False
                    self.info("No uart peripheral '{}' found.".format(self._search_name))
            elif self.connecting_lego:
                if self._addr_type is not None:
                    print("Found SMART Hub:", self._name)
                    sleep_ms(500)
                    self._ble.gap_connect(self._addr_type, self._addr)
                else:
                    self.connecting_lego = False
                    self.info("LEGO Smart hub found.")
            if self._scan_done_callback:
                self._scan_done_callback(data)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect to peripheral successful.
            conn_handle, addr_type, addr = data
            if self.connecting_uart:
                self._conn_handle=conn_handle
            elif self.connecting_lego:
                self._lego_conn_handle=conn_handle
            self._ble.gattc_discover_services(conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if self._disconn_callback:
                self._disconn_callback(conn_handle)

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            if uuid == _UART_UUID or uuid == _LEGO_SERVICE_UUID:
                # Save handles until SERVICE_DONE
                self._start_handle = start_handle
                self._end_handle = end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                self.info("Failed to find requested gatt service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if self.connecting_uart:
                if uuid == _UART_RX_UUID:
                    self._rx_handle = value_handle
                elif uuid == _UART_TX_UUID:
                    self._tx_handle = value_handle
                if all((self._conn_handle, self._rx_handle, self._tx_handle)):
                    self.connecting_uart = False
            elif self.connecting_lego:
                if uuid == _LEGO_SERVICE_CHAR:
                    self._lego_value_handle = value_handle
                    self.connecting_lego = False # We're done
            if self._char_result_callback:
                self._char_result_callback(conn_handle, value_handle, uuid)

        # elif event == _IRQ_GATTC_WRITE_DONE:
        #    conn_handle, value_handle, status = data
        #    # print("TX complete")

        elif event == _IRQ_GATTC_NOTIFY:
            # print("_IRQ_GATTC_NOTIFY")
            conn_handle, value_handle, notify_data = data
            notify_data=bytes(notify_data)
            if conn_handle in self._notify_callbacks.keys():
                schedule(self._notify_callbacks[conn_handle],notify_data)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A read completed successfully.
            #print("_IRQ_GATTC_READ_RESULT")
            conn_handle, value_handle, char_data = data
            self._read_data = bytes(char_data)
            if self._reading == conn_handle: self._reading = False
            if self._read_callback:
                self._read_callback(data)

        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            print("New connection", conn_handle)
            self._connected_centrals.add(conn_handle)
            if self._central_conn_callback:
                self._central_conn_callback(data)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("Disconnected", conn_handle)
            # self._connected_centrals.remove(conn_handle)
            if self._central_disconn_callback:
                self._central_disconn_callback(data)

        elif event == _IRQ_GATTS_WRITE:
            # A central has written to the 'value handle' peripheral(?) characteristic.
            # Get the value and trigger the callback.
            # TODO: Test if peripherals can also write to centrals or whether they can only indicate.
            conn_handle, value_handle = data
            if value_handle in self._write_callbacks:
                value = self._ble.gatts_read(value_handle)
                self._write_callbacks[value_handle](value)

        else:
            self.info("Unhandled event, no problem: ", hex(event), "data:", data)

    def discover_characteristics(self, args):
        self._ble.gattc_discover_characteristics(*args)

    def advertise(self, payload, interval_us=100000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=payload)

    def on_write(self, value_handle, callback):
        self._write_callbacks[value_handle] = callback

    def notify(self, data, handle):
        # Notify all connected centrals interested in the handle
        for conn_handle in self._connected_centrals:
            self._ble.gatts_notify(conn_handle, handle, data)

    def register_uart_service(self):
        ((handle_tx, handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # set max message size to 100 bytes
        self._ble.gatts_write(handle_rx, bytes(100))
        self._ble.gatts_set_buffer(handle_rx, 100)
        self._ble.gatts_set_buffer(handle_tx, 100)
        return handle_tx, handle_rx

    # Find a device advertising the uart service.
    def scan(self):
        self._ble.gap_scan(20000, 30000, 30000)

    def stop_scan(self):
        self._ble.gap_scan(None)

    def connect_uart(self, name="robot"):
        self._search_name = name
        # self.timed_out = False
        self.connecting_uart = True
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._rx_handle = None
        self._tx_handle = None
        self._addr_type = None
        self._addr = None
        self.scan()
        for i in range(20):
            print("Waiting for connection...")
            sleep_ms(500)
            if (not self.connecting_uart): # or (self._conn_handle):
                break
        return self._conn_handle

    def connect_lego(self):
        self.connecting_lego = True
        self._lego_conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._lego_value_handle = None
        self._addr_type = None
        self._addr = None
        self._addr_type = None
        self._addr = None
        self.scan()
        for i in range(20):
            print("Waiting for connection...")
            sleep_ms(500)
            if (not self.connecting_lego): # or (self.timed_out):
                break
        return self._lego_conn_handle

    def uart_write(self, value, conn_handle=None, response=False):
        if not conn_handle: conn_handle = self._conn_handle
        self._ble.gattc_write(conn_handle, self._rx_handle, value, 1 if response else 0)

    def read(self, conn_handle, val_handle, callback=None):
        self._read_callback = callback
        try:
            self._ble.gattc_read(conn_handle, val_handle)
        except Exception as e:
            print("gattc_read failed",e)

    def uart_read(self, conn_handle=None):
        if not conn_handle: conn_handle = self._conn_handle
        self._reading = conn_handle
        self.read(conn_handle, self._tx_handle)
        n=0
        for i in range(100):
            if not self._reading:
                n = i
                break
            sleep_ms(4)
        print("n:",n)
        return self._read_data

    def lego_read(self, conn_handle=None):
        if not conn_handle: conn_handle = self._lego_conn_handle
        self._reading = conn_handle
        self.read(conn_handle, self._lego_value_handle)
        n=0
        for i in range(100):
            if not self._reading:
                n = i
                break
            sleep_ms(4)
        # print("n:",n)
        return self._read_data

    def lego_write(self, value, conn_handle=None, response=False):
        if not conn_handle: conn_handle = self._lego_conn_handle
        if self._lego_value_handle:
            self._ble.gattc_write(conn_handle, self._lego_value_handle, value, 1 if response else 0)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type, addr):
        self._ble.gap_connect(addr_type, addr)

    def disconnect(self, conn_handle):
        self._ble.gap_disconnect(conn_handle)

    def enable_notify(self, conn_handle, desc_handle, callback=None):
        self._ble.gattc_write(conn_handle, desc_handle, struct.pack('<h', _NOTIFY_ENABLE), 0)
        if callback:
            self._notify_callbacks[conn_handle] = callback


class UARTPeripheral():
    def __init__(self, ble_handler:BLEHandler=None, name="robot", buffered=False):
        self.name = name
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler
        self._handle_tx, self._handle_rx = ble_handler.register_uart_service()
        self.ble_handler.on_write(self._handle_rx, self.on_rx)
        self.ble_handler._central_conn_callback = self.on_connect
        self.ble_handler._central_disconn_callback = self.on_disconnect
        self.connected = False
        self.buffered = buffered
        self.buffer = bytearray()
        self.on_disconnect()

    def is_connected(self):
        return self.connected

    def on_disconnect(self, *data):
        self.connected = False
        self.ble_handler.advertise(advertising_payload(name=self.name, services=[_UART_UUID]))

    def on_connect(self, *data):
        self.connected = True
        # Is this necessary? Trying without.
        # self.ble_handler.on_write(self._handle_rx, self.on_rx)

    def on_rx(self, data):
        if self.buffered:
            self.buffer += data
        else:
            self.buffer = data

    def any(self):
        return len(self.buffer)

    def read(self, n=-1):
        if not self.buffered:
            return self.buffer
        else:
            bufsize = len(self.buffer)
            if n < 0 or n > bufsize:
                n = bufsize
            data = self.buffer[:n]
            del self.buffer[:n]
            return data

    def write(self, data):
        # Maybe this should be indicate instead.
        self.ble_handler.uart_write(data)


class RCReceiver(UARTPeripheral):
    def __init__(self, ble_handler:BLEHandler=None, name="robot", logo="00000:05550:05950:05550:00000"):
        self._logo=Image(logo)
        self._CONNECT_ANIMATION = [img + self._logo for img in _CONNECT_IMAGES]
        super().__init__(ble_handler, name)
        self.buffer = bytearray(struct.calcsize("bbbbBBhhB"))

    def button_pressed(self, button):
        # Test if any buttons are pressed on the remote
        if 0 < button < 9:
            return self.controller_state(BUTTONS) & 1 << button-1
        else:
            return False

    def on_disconnect(self, *data):
        display.show(self._CONNECT_ANIMATION, delay=100, wait=False, loop=True)
        super().on_disconnect(*data)

    def on_connect(self, *data):
        display.show(self._logo)
        # TODO: This is nasty. Should be self.write()
        # The delay is there to come after the char discovery phase.
        t = Timer(
            mode=Timer.ONE_SHOT,
            period=2000,
            callback=lambda x:self.ble_handler.notify(repr(self._logo), self._handle_tx)
            )
        super().on_connect(*data)

    def controller_state(self, *indices):
        try:
            controller_state = struct.unpack("bbbbBBhhB", self.buffer)
        except:
            controller_state = [0]*9
        if indices:
            if len(indices) is 1:
                return controller_state[indices[0]]
            else:
                return [controller_state[i] for i in indices]
        else:
            return controller_state
        

HUB_NOTIFY_DESC = const(0x0F)
REMOTE_NOTIFY_DESC = const(0x0C)
MARIO_NOTIFY_DESC = const(14)
HUB_PORT_ACC = const(0x61)
HUB_PORT_GYRO = const(0x62)
HUB_PORT_TILT = const(0x63)

MODE = const(0)
MODE_BYTE = const(1)
MODE_DATA_SETS = const(2)
MODE_DATA_SET_TYPE = const(3)

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

    def connected(self):
        return self._conn_handle is not None

    def connect(self):
        self._conn_handle = self.ble_handler.connect_lego()
        if self._conn_handle:
            sleep_ms(500)
            # Subscribe to motion data of SMART Hubs
            self.write(0x0A, 0x00, 0x41, HUB_PORT_ACC, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)
            self.write(0x0A, 0x00, 0x41, HUB_PORT_GYRO, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)
            self.write(0x0A, 0x00, 0x41, HUB_PORT_TILT, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01)
            sleep_ms(200)

            # Initialize all ports with mode 0
            SET_MODE = 0
            for i in range(4):
                # SUBSCRIBE_MODE
                self.write(0x0A,0x00,0x41, i, SET_MODE, 0x01, 0x00, 0x00, 0x00, 0x01)
                sleep_ms(100)
                # GET_MODE_INFO
                self.write(0x06, 0x00, 0x22, i, SET_MODE, 0x80)
                sleep_ms(100)

            # Enable notify on smart hubs
            self.ble_handler.enable_notify(self._conn_handle, HUB_NOTIFY_DESC, self.__on_notify)
            sleep_ms(200)
            self.set_led_color(GREEN)
        else:
            print("Connection failed")

    def disconnect(self):
        if self._conn_handle:
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
                MODE : payload[0],
                MODE_BYTE : payload[1],
                MODE_DATA_SETS : payload[2],
                MODE_DATA_SET_TYPE : payload[3],
            }

    def unpack_data(self, port, fmt="3h"):
        if port in self.hub_data.keys():
            return struct.unpack(fmt, self.hub_data[port])

    def acc(self):
        return self.unpack_data(HUB_PORT_ACC)

    def gyro(self):
        return self.unpack_data(HUB_PORT_GYRO)

    def tilt(self):
        return self.unpack_data(HUB_PORT_TILT)

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
                data_set_type = self.mode_info[port][MODE_DATA_SET_TYPE]
                no_data_sets = self.mode_info[port][MODE_DATA_SETS]

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


class RCTransmitter():
    def __init__(self, ble_handler:BLEHandler=None):
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler
        self.controller_state = [0]*9
        self._reset()

    def _reset(self):
        self._addr_type = None
        self._addr = None
        self._conn_handle = None
        self._tx_handle = 9
        self._rx_handle = 12

    def _on_disconnect(self, conn_handle):
        if conn_handle == self._conn_handle:
            # If it was initiated by us, it'll already be reset.
            self._reset()
            print("Disconnected by peripheral")

    def connect(self, name="robot"):
        self.ble_handler._disconn_callback = self._on_disconnect
        self._conn_handle = self.ble_handler.connect_uart(name)
        return self.is_connected()

    # Returns true if we've successfully connected and discovered uart characteristics.
    def is_connected(self):
        return self._conn_handle is not None

    # Disconnect from current device.
    def disconnect(self):
        if self._conn_handle:
            self.ble_handler.disconnect(self._conn_handle)
            self._reset()

    def set_button(self, num, pressed):
        if 0 < num < 9:
            bitmask = 0b1 << (num-1)
            if pressed:
                self.controller_state[BUTTONS] |= bitmask
            else:
                self.controller_state[BUTTONS] &= ~bitmask

    def set_stick(self, stick, value):
        self.controller_state[stick] = clamp_int(value)

    def set_trigger(self, trig, value):
        self.controller_state[trig] = clamp_int(value,0,200)

    def set_setting(self, stick, value):
        self.controller_state[stick] = clamp_int(value, -2**15, 2**15)

    # Send data over the UART
    def transmit(self):
        if not self.is_connected():
            print("Can't transmit, not connected")
            return
        value = struct.pack("bbbbBBhhB", *self.controller_state)
        self.ble_handler.uart_write(value, self._conn_handle)
        
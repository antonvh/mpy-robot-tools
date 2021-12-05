from hub import display, Image
import bluetooth
import struct
from time import sleep_ms
from micropython import const
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
        self._notify_callback = None
        self._search_name = None
        self.connecting_uart = False
        self.connecting_lego = False

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
                    self._name = self.__decoder.decode_name(adv_data)
                    self._services = self.__decoder.decode_services(adv_data)
                    self._man_data = self.__decoder.decode_manufacturer(adv_data)
            if self._scan_result_callback:
                self._scan_result_callback(addr_type, addr, name, services)

        # elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
        #     # Called once service discovery is complete.
        #     # Note: Status will be zero on success, implementation-specific value otherwise.
        #     # conn_handle, status = data
        #     pass

        elif event == _IRQ_SCAN_DONE:
            if self.connecting_uart:
                if self._addr_type is not None:
                    print("Found peripheral:", self._search_name)
                    sleep_ms(500)
                    self._ble.gap_connect(self._addr_type, self._addr)
                else:
                    self.connecting_uart = False
                    # print("No uart peripheral '{}' found.".format(self._search_name))
            if self._scan_done_callback:
                self._scan_done_callback(data)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect successful.
            conn_handle, addr_type, addr = data
            self._conn_handle=conn_handle
            self._ble.gattc_discover_services(conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if self._disconn_callback:
                self._disconn_callback(conn_handle)

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            if uuid == _UART_UUID:
                # self._start_handle, self._end_handle = start_handle, end_handle
                # print("UART_UID handles",data)
                sleep_ms(500)
                try:
                    self._ble.gattc_discover_characteristics(conn_handle, start_handle, end_handle)
                except:
                    pass

        # elif event == _IRQ_GATTC_SERVICE_DONE:
        #     # Service query complete.
        #     # if self._start_handle and self._end_handle:
        #     #    # This is called at result and at done. Probably once too much.
        #     #    self._ble.gattc_discover_characteristics(
        #     #        self._conn_handle, self._start_handle, self._end_handle
        #     #    )
        #     # else:
        #     #    print("Failed to find uart service.")
        #     #    self.timed_out = True

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
            if self._char_result_callback:
                self._char_result_callback(conn_handle, value_handle, uuid)

        # elif event == _IRQ_GATTC_WRITE_DONE:
        #     conn_handle, value_handle, status = data
        #     # print("TX complete")

        elif event == _IRQ_GATTC_NOTIFY:
            # print("_IRQ_GATTC_NOTIFY")
            conn_handle, value_handle, notify_data = data
            notify_data=bytes(notify_data)

            # if conn_handle == self._conn_handle and value_handle == self._tx_handle:
            if self._notify_callback:
                self._notify_callback(conn_handle, value_handle, notify_data)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A read completed successfully.
            #print("_IRQ_GATTC_READ_RESULT")
            conn_handle, value_handle, char_data = data
            if conn_handle == self._conn_handle and value_handle in (self._rx_handle,self._buta_handle,self._butb_handle):
                # print("handle,READ data",value_handle,bytes(char_data))
                self._read_callback(value_handle,bytes(char_data))

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
            conn_handle, value_handle = data
            # print(value_handle, self._write_callbacks)
            if value_handle in self._write_callbacks:
                value = self._ble.gatts_read(value_handle)
                self._write_callbacks[value_handle](value)

        else:
            self.info("Unhandled event, no problem: ", event, hex(event))


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
        self._rx_handle = None
        self._tx_handle = None
        self._addr_type = None
        self._addr = None
        self.scan()
        for i in range(20):
            print("Waiting for connection...")
            sleep_ms(500)
            if (not self.connecting_uart): # or (self.timed_out):
                break
        return self._conn_handle

    def uart_write(self, conn_handle, value, response=False):
        self._ble.gattc_write(conn_handle, self._rx_handle, value, 1 if response else 0)

    def uart_read(self, conn_handle, callback):
        self._read_callback = callback
        try:
            self._ble.gattc_read(conn_handle, self._tx_handle)
        except:
            pass
            print("gattc_read failed")

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type, addr):
        self._ble.gap_connect(addr_type, addr)

    def disconnect(self, conn_handle):
        self._ble.gap_disconnect(conn_handle)

    # def enable_notify(self):
    #    if not self.is_connected():
    #        return
    #    print("Enabled notify")
    #    #self._ble.gattc_write(self._conn_handle, self._acc_handle, struct.pack('<h', _NOTIFY_ENABLE), 0)
    #    for i in range(38,49):
    #        self._ble.gattc_write(self._conn_handle, i, struct.pack('<h', _NOTIFY_ENABLE), 0)
    #        time.sleep_ms(50)
    #    print("notified enabled")

class RCReceiver:
    def __init__(self, ble_handler:BLEHandler=None, name="robot", logo="00000:05550:05950:05550:00000"):
        self._logo=Image(logo)
        self.name = name
        self._CONNECT_ANIMATION = [img + self._logo for img in _CONNECT_IMAGES]
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler
        self._handle_tx, self._handle_rx = ble_handler.register_uart_service()
        self.controller_state = [0]*9
        self.ble_handler.on_write(self._handle_rx, self.on_rx)
        self.ble_handler._central_conn_callback = self.on_connect
        self.ble_handler._central_disconn_callback = self.on_disconnect
        self.connected = False
        self.on_disconnect()

    def button_pressed(self, button):
        # Test if any buttons are pressed on the remote
        return self.controller_state[BUTTONS] & 1 << button-1

    def on_disconnect(self, *data):
        display.show(self._CONNECT_ANIMATION, delay=100, wait=False, loop=True)
        self.connected = False
        self.ble_handler.advertise(advertising_payload(name=self.name, services=[_UART_UUID]))

    def on_connect(self, data):
        display.show(self._logo)
        self.connected = True
        self.ble_handler.on_write(self._handle_rx, self.on_rx)
        t = Timer(
            mode=Timer.ONE_SHOT,
            period=2000,
            callback=lambda x:self.ble_handler.notify(repr(self._logo), self._handle_tx)
            )

    def on_rx(self, control):
        # Remote control data callback function
        self.controller_state = struct.unpack("bbbbBBhhB", control)


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
        self.ble_handler.uart_write(self._conn_handle, value)
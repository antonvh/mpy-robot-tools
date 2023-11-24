### Bluetooth Low Energy (BLE) connection and communication tools 
### for MINDSTORMS robots and LMS-ESP32
### Supports Midi, Nordic UART, BLE Remote app, and LEGO Protocol: LPF2/LPUP/CTRL-PLUS.

### (c) 2023 Anton's Mindstorms & Ste7an

# Warning! This does NOT work on SPIKE Prime firmware.
# Flash your SPIKE Prime with MINDSTORMS firmware if you want to use bluetooth.
# See https://docs.antonsmindstorms.com for tutorial and explanation.

## TODO
## Fix occasional packet loss on very large notify payloads:
## Maybe notify size or delay
## Write blog post about ble and uart and the misery.
## Create SerialTalk example.
## Clean up Ble_handler: Move connection code to LEGO and UART classes.
## Try gc.collect() in every loop?
## Fix mem allocation and scheduling in IRQ's:
# Note: If schedule() is called from a preempting IRQ,
# when memory allocation is not allowed and the callback
# to be passed to schedule() is a bound method, passing this
# directly will fail. This is because creating a reference to a
# bound method causes memory allocation. A solution is to
# create a reference to the method in the class constructor
# and to pass that reference to schedule().
# This is discussed in detail here reference documentation under “Creation of Python objects”.

try:
    from utime import sleep_ms, ticks_diff, ticks_ms
    from micropython import const, schedule, alloc_emergency_exception_buf
    import ubluetooth
    import struct
    alloc_emergency_exception_buf(100)
    if not 'FLAG_INDICATE' in dir(ubluetooth):
        # We're on SPIKE Prime, old version of ubluetooth
        print("WARNING SPIKE Prime not supported for Ble. Use MINDSTORMS Firmware.")
        raise Exception("Firmware not supported")
except:
    # Polyfill for automated testing purposes
    class ubluetooth():
        def UUID(_):
            pass
    print("Import failed. Not on micropython?")

TARGET_MTU = const(184) # Try to negotiate this packet size for UART
MAX_NOTIFY = const(100) # Somehow notify with the full mtu is unstable. Memory issue?


L_STICK_HOR = const(0)
L_STICK_VER = const(1)
R_STICK_HOR = const(2)
R_STICK_VER = const(3)
L_TRIGGER = const(4)
R_TRIGGER = const(5)
SETTING1 = const(6)
SETTING2 = const(7)
BUTTONS = const(8)

_NOTIFY_ENABLE = const(1)
_INDICATE_ENABLE = const(2)
_FLAG_READ = 0x02
_FLAG_WRITE_NO_RESPONSE = 0x04
_FLAG_WRITE = 0x08
_FLAG_NOTIFY = 0x10
_FLAG_INDICATE = 0x20

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_MTU_EXCHANGED = const(21)


# Helpers for generating BLE advertising payloads.
# Advertising payloads are repeated packets of the following form:
# 1 byte data length (N + 1)
# 1 byte type (see constants below)
# N bytes type-specific data

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
# _ADV_TYPE_UUID16_MORE = const(0x2)
# _ADV_TYPE_UUID32_MORE = const(0x4)
# _ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)

# UART
_UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_UUID = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    _UART_TX_UUID,
    _FLAG_NOTIFY | _FLAG_READ, # write is not really needed here.
)
_UART_RX = (
    _UART_RX_UUID,
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE, # read should not be needed here.
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# LEGO
_LEGO_SERVICE_UUID = ubluetooth.UUID("00001623-1212-EFDE-1623-785FEABCD123")
_LEGO_SERVICE_CHAR = ubluetooth.UUID("00001624-1212-EFDE-1623-785FEABCD123")

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


def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    """
    Generate advertising payload.

    :param limited_disc: Limited discoverable mode. Determines whether the device can be discoverable for a limited period. Default value is ``False``.
    :type limited_disc: bool
    :param br_edr: BR/EDR support (Basic Rate/Enhanced Data Rate). Determines whether the device supports classic Bluetooth. Default value is ``False``.
    :type br_edr: bool
    :param name: Name of the device to be advertised. Default value is ``None``.
    :type name: str
    :param services: List of services offered by the device, typically identified by UUIDs. Default value is ``None``.
    :type services: list
    :param appearance: Appearance category code, describing the visual appearance of the device (e.g., phone, keyboard). Default value is ``False``.
    :type appearance: int
    :return: An array of bytes with the specified payload.
    :rtype: list[bytes]
    """

    payload = bytearray()

    def _append(adv_type, value):
        """Auxiliary function to populate the payload array"""
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


def _decode_field(payload, adv_type):
    """
    Decode field from BLE Advertising payload.

    :param payload: Payload of the message.
    :type payload: bytearray
    :param adv_type: Type of the field to decode. See constants starting with ``_ADV_TYPE_`` for possible values.
    :type adv_type: int
    :return: An list with the decoded field values.
    """
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2: i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def _decode_name(payload):
    """
    Decode name from BLE Advertising payload.

    :param payload: Payload of the message.
    :type payload: bytearray
    """
    n = _decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], "utf-8") if n else ""


def _decode_services(payload):
    """
    Decode service UUIDs from BLE Advertising payload.

    :param payload: Payload of the message.
    :type payload: bytearray

    :return: A list of UUID objects representing the services.
    """
    services = []
    for u in _decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(ubluetooth.UUID(struct.unpack("<h", u)[0]))
    for u in _decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(ubluetooth.UUID(struct.unpack("<d", u)[0]))
    for u in _decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(ubluetooth.UUID(u))
    return services


class BLEHandler:
    """
    Basic Bluetooth Low Energy class that can be a central or peripheral or both.
    The central always connects to a peripheral. The Peripheral just advertises.
    Instantiate a BLEHandler and pass it to the UARTCentral and UARTPeripheral class,
    if you want to use both classes on the same device.

    :param debug: Keep a log of events in the log property. WARNING: Debug log is kept in memory. Long transactions will lead to memory errors!
    :type debug: bool
    """

    def __init__(self, debug=False):
        self._ble = ubluetooth.BLE()
        self._ble.config(rxbuf=TARGET_MTU)
        self._ble.active(True)
        try:
            self._ble.gap_disconnect(1025) # Disconnect in case of previous crash
        except:
            pass
        self._ble.irq(self._irq)
        self.debug = debug
        self.log_size = 200
        self._reset()

    def _reset(self):
        self._connected_central = -1    # Only one central can connect. -1 is not connected.
        self._scan_result_callback = None
        self._scan_done_callback = None
        self._write_done_callbacks = {}
        self._disconn_callbacks = {}
        self._central_conn_callback = None      # Used when centrals connect
        self._central_disconn_callback = None   # Used when centrals disconnect
        self._char_result_callback = None
        self._write_callbacks = {}
        self._notify_callbacks = {}
        self._search_name = None
        self.connecting_uart = False
        self.connecting_lego = False
        self._read_data = {}
        self._start_handle = None
        self._end_handle = None
        self.mtu = 20
        if self.debug:
            # Reserve log_size bytes and track the index of the last written byte.
            self.log_data = bytearray(self.log_size)
            self.log_idx = 0
        else:
            self.log_data = b''

    def info(self, *messages):
        """
        Saves messages to the log if debug is enabled. 

        :param messages: Messages to save to the log
        :type messages: str


        :Example:

        .. code-block:: python

            self.info(var1, var2, var3)
        """

        if self.debug:
            for m in messages:
                d = bytes(str(m),'utf8')
                l = len(d)
                if self.log_idx+l>self.log_size:
                    self.log_idx = 0
                self.log_data[self.log_idx:self.log_idx+l]=d
                self.log_idx += l
            if self.log_idx < self.log_size:
                self.log_data[self.log_idx]=10 #10 is ascii for \n newline
                self.log_idx += 1
            else:
                self.log_idx = 0

    def print_log(self):
        """Prints the log to the console and clears it."""
        for l in self.log_data[self.log_idx:].decode('utf8').split('\n'):
            print(l)
        for l in self.log_data[:self.log_idx].decode('utf8').split('\n'):
            print(l)
        self.log_data=bytearray(self.log_size)
        self.log_idx=0

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            name = _decode_name(adv_data) or "?"
            services = _decode_services(adv_data)
            # self.info(self._search_payload == adv_data) # This works TODO: Implement properly
            self.info("Found: ", name, " with services: ", services)
            if self.connecting_uart:
                if name == self._search_name and _UART_UUID in services:
                    # Found a potential device, remember it
                    self._addr_type = addr_type
                    self._addr = bytes(addr)# Note: addr buffer is owned by caller so need to copy it.
                    # ... and stop scanning. This triggers the IRQ_SCAN_DONE and the on_scan callback.
                    self.stop_scan()
            if self.connecting_lego:
                if _LEGO_SERVICE_UUID in services:
                    self._addr_type = addr_type
                    self._addr = bytes(addr)
                    self._adv_type = adv_type
                    self._name = _decode_name(adv_data)
                    self._services = _decode_services(adv_data)
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
            if self.connecting_uart or self.connecting_lego:
                self._conn_handle = conn_handle
            self._ble.gattc_discover_services(conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if conn_handle in self._disconn_callbacks:
                if self._disconn_callbacks[conn_handle]:
                    self._disconn_callbacks[conn_handle]()
                    # TODO Also delete any notify callbacks

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

        elif event == _IRQ_MTU_EXCHANGED:
            # A remote central negotiated a new mtu
            # Store it to control large transfers
            # TODO: find out if mtu is conn_handle dependent...
            # Let's assume it isn't.
            conn_handle, mtu = data
            self.mtu = mtu
            self.info("Mtu:", mtu)

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
                    self.connecting_lego = False# We're done
            if self._char_result_callback:
                self._char_result_callback(conn_handle, value_handle, uuid)

        elif event == _IRQ_GATTC_WRITE_DONE:
            # This event fires in a central, when it is done writing
            # to a remote peripheral.
            # Call the callback on the value handle that has finished if there is one.
            # The callback function should check for the value handle.
            conn_handle, value_handle, status = data
            self.info("Write done on", conn_handle, "in value", value_handle)
            if conn_handle in self._write_done_callbacks:
                self._write_done_callbacks[conn_handle](value_handle, status)

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            notify_data = bytes(notify_data)
            self.info("Notify:", conn_handle, value_handle, notify_data)
            if conn_handle in self._notify_callbacks:
                if self._notify_callbacks[conn_handle]:
                    schedule(self._notify_callbacks[conn_handle], notify_data)

        elif event == _IRQ_GATTC_READ_RESULT:
            # A read completed successfully and returns data
            conn_handle, value_handle, char_data = data
            char_data = bytes(char_data)
            self.info("Read:", conn_handle, value_handle, char_data)
            self._read_data[(value_handle << 12) + conn_handle] = char_data

        elif event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.info("New connection ", conn_handle)
            self._connected_central = conn_handle
            if self._central_conn_callback:
                self._central_conn_callback(*data)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.info("Disconnected ", conn_handle)
            self._connected_central = -1
            if self._central_disconn_callback:
                self._central_disconn_callback(conn_handle)

        elif event == _IRQ_GATTS_WRITE:
            # A client/central has written to a characteristic or descriptor.
            # Get the value and trigger the callback.
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            self.info("Client/central wrote:", conn_handle, value)
            if value_handle in self._write_callbacks:
                if self._write_callbacks[value_handle]:
                    self._write_callbacks[value_handle](value)

        else:
            self.info("Unhandled event: ", hex(event), "data:", data)

    def advertise(self, payload, interval_us=100000):
        """
        Advertise a BLE payload for a given time interval.
        Create the payload with the _advertising_payload() function.
        """
        print("Started advertising")
        self._ble.gap_advertise(interval_us, adv_data=payload)

    def on_write(self, value_handle, callback):
        """
        Register a callback on the peripheral (server) side for when a client (central) writes to a characteristic or descriptor.
        It's time to process the received data!

        :param value_handle: The handle of the characteristic or descriptor to register the callback for.
        :type value_handle: int
        :param callback: The callback function to call when a client writes to the characteristic or descriptor.
        :type callback: function
        """
        self._write_callbacks[value_handle] = callback

    def on_write_done(self, conn_handle, callback):
        """
        Register a client (central) callback for when that client (central) is done writing to a characteristic or descriptor.
        This helps you to avoid writing too much data to the peripheral too soon.

        :param conn_handle: The handle of the connection to register the callback for.
        :type conn_handle: int
        :param callback: The callback function to call when a client writes to the characteristic or descriptor.
        :type callback: function
        """
        self._write_done_callbacks[conn_handle] = callback

    def notify(self, data, val_handle, conn_handle=None):
        """
        Notify connected central interested in the value handle,
        with the given data. gatts_notify is similar to gatts_indicate, but has not
        acknowledgement, and thus raises no _IRQ_GATSS_INDICATE_DONE.

        :param data: The data to send to the central(s).
        :type data: bytes
        :param val_handle: The handle of the characteristic or descriptor to notify.
        :type val_handle: int
        :param conn_handle: The handle of the connection to notify. If None, notify all connected centrals.
        """
        self._ble.gatts_write(val_handle, data)
        # No send_update=True in gatts_write in the Inventor firmware, so notifying explicitly:
        if conn_handle is not None:
            self._ble.gatts_notify(conn_handle, val_handle)
        elif self._connected_central >= 0:
            self._ble.gatts_notify(self._connected_central, val_handle)

    def scan(self):
        """
        Start scanning for BLE peripherals. Scan results will be returned in the IRQ handler.
        """
        self._ble.gap_scan(20000, 30000, 30000)

    def stop_scan(self):
        """
        Stop scanning for BLE peripherals.
        """
        self._ble.gap_scan(None)

    def connect_uart(self, name="robot", on_disconnect=None, on_notify=None, on_write_done=None, time_out=10):
        """
        Connect to a BLE Peripheral that advertises with a certain name, and has a UART service.
        This method is meant for BLE Centrals

        :param name: The name of the peripheral to search for and connect to
        :type name: str
        :param on_disconnect: Callback function to call when the peripheral disconnects
        :type on_disconnect: function
        :param on_notify: Callback function to call when the peripheral notifies the central
        :type on_notify: function
        :param on_write_done: Callback function to call when the peripheral is done writing to the central
        :type on_write_done: function
        """
        # TODO: Create a generic connecting function that encodes the searched-for advertising data
        # self._search_payload = _advertising_payload(name=name, services=[_UART_UUID])
        # and searches for a match. 
        # Then make connect_uart and connect_lego call that DRYer function.

        self._search_name = name
        self.connecting_uart = True
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._rx_handle = None
        self._tx_handle = None
        self._addr_type = None
        self._addr = None
        
        self.scan()
        for i in range(time_out):
            
            if self.debug:
                self.print_log()
            else:
                print("Connecting to UART Peripheral:", name)
            sleep_ms(1000)
            if not self.connecting_uart:
                break
        if self._rx_handle:
            self._notify_callbacks[self._conn_handle] = on_notify
            self._disconn_callbacks[self._conn_handle] = on_disconnect
            self._write_done_callbacks[self._conn_handle] = on_write_done

            # Increase packet size
            self._ble.config(mtu=TARGET_MTU)
            self._ble.gattc_exchange_mtu(self._conn_handle)
            sleep_ms(60)
            # Store the result of the mtu negotiation.
            self.mtu=self._ble.config("mtu")-4 # Some overhead bytes in max msg size.

        self.connecting_uart = False
        return self._conn_handle, self._rx_handle, self._tx_handle

    def connect_lego(self, time_out=10):
        """
        Connect to a LEGO Smart Hub that advertises with a LEGO service.
        LEGO Hubs are advertising when their leds are blinking, just after turning them on.
        """
        self.connecting_lego = True
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._lego_value_handle = None
        self._addr_type = None
        self._addr = None
        self.scan()
        for i in range(time_out):
            if self.debug:
                self.print_log()
            else:
                print("Connecting to a LEGO Smart Hub...")
            sleep_ms(1000)
            if not self.connecting_lego:
                break
        self.connecting_lego = False
        return self._conn_handle

    def uart_write(self, value, conn_handle, rx_handle=12, response=False):
        self._ble.gattc_write(conn_handle, rx_handle, value, 1 if response else 0)
        self.info("GATTC Written ", value)

    def lego_write(self, value, conn_handle=None, response=False):
        if not conn_handle: conn_handle = self._conn_handle
        if self._lego_value_handle and conn_handle is not None:
            self._ble.gattc_write(conn_handle, self._lego_value_handle, value, 1 if response else 0)
            self.info("GATTC Written ", value)




    def enable_notify(self, conn_handle, desc_handle, callback=None):
        self._ble.gattc_write(conn_handle, desc_handle, struct.pack('<h', _NOTIFY_ENABLE), 0)
        if callback:
            self._notify_callbacks[conn_handle] = callback


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
    
    def write_midi_notes(self, notes, velocity=0, on=True, channel=0):
        """
        Timestamps and writes multiple MIDI notes to the BLE GATT server.

        :param notes: list of MIDI note numbers
        :type notes: bytearray or list of int
        :param velocity: velocity
        :type velocity: byte or int
        :param on: Turn notes on if True, off if false. Default True.
        :type on: bool
        :param channel: MIDI Channel, default 0
        :type channel: int
        """
        d = bytearray(3+2*len(notes))
        timestamp_ms = ticks_ms()
        d[0] = (timestamp_ms >> 7 & 0x3F) | 0x80
        d[1] = 0x80 | (timestamp_ms & 0x7F)
        d[2] = 0x90 + channel if on else 0x80 + channel
        for i in range(len(notes)):
            d[3 + i*2] = notes[i]
            d[4 + i*2] = velocity
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
        base = note_parser(base)
        notes = [base+offset for offset in CHORD_STYLES[style]]
        self.write_midi_notes(notes, velocity)

    def chord_off(self, base, velocity=0, style="M"):
        """
        Stop playing a MIDI chord.
        """
        base = note_parser(base)
        notes = [base+offset for offset in CHORD_STYLES[style]]
        self.write_midi_notes(notes, velocity, on=False)

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


class BleUARTBase:
    """
    Base class with a buffer for UART methods any(), read()
    """
    READS_PER_MS = 10

    def __init__(self, additive_buffer=True):
        self.additive_buffer = additive_buffer
        self.read_buffer = b''

    def _on_rx(self, data):
        if data:
            if self.additive_buffer:
                self.read_buffer += data
            else:
                self.read_buffer = data

    def any(self):
        """
        Returns the number of bytes in the read buffer.
        """
        return len(self.read_buffer)

    def read(self, n=-1):
        """
        Read data from remote.

        :param n: The number of bytes to read. If n is negative or omitted, read all data available.
        :type n: int
        """
        bufsize = len(self.read_buffer)
        if n < 0 or n > bufsize:
            n = bufsize
        data = self.read_buffer[:n]
        self.read_buffer = self.read_buffer[n:]
        return data

    def readline(self):
        """
        Read a line from remote. A line is terminated with a newline character. ``\\n``
        """
        data = b''
        tries = 0
        while tries < 50: # 1s timeout
            c = self.read(1)
            if c == b'\n':
                break
            elif c == b'':
                if not self.is_connected() : break
                tries += 1
                sleep_ms(25)
            else:
                tries = 0
                data += c
        return data.decode("UTF")

    def writeline(self, data: str):
        """
        Write data to remote and terminate with an added newline character. ``\\n``
        """
        self.write(data+"\n")


class UARTPeripheral(BleUARTBase):
    """
    Class for a Nordic UART BLE server/peripheral.
    It will advertise as the given name and populate the UART services and characteristics

    :param name: The name of the peripheral
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    :param additive_buffer: If True, the read buffer will be added to on each read. If False, the read buffer will be overwritten on each read.
    :type additive_buffer: bool
    """

    def __init__(self, name="robot", ble_handler: BLEHandler = None, additive_buffer=True):
        super().__init__(additive_buffer)
        self.name = name
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler

        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        self.ble_handler.on_write(self._handle_rx, self._on_rx)
        self.ble_handler_central_disconn_callback = self._on_disconnect

        # Characteristics and descriptors have a default maximum size of 20 bytes.
        # Anything written to them by a client will be truncated to this length.
        # However, any local write will increase the maximum size, so if you want
        # to allow larger writes from a client to a given characteristic,
        # use gatts_write after registration.

        # Increase buffer size to fit MTU
        self._ble.gatts_set_buffer(self._handle_rx, TARGET_MTU)

        # Stretch buffer
        self._ble.gatts_write(self._handle_rx, bytes(TARGET_MTU))

        # Flush
        _ = self._ble.gatts_read(self._handle_rx)
        self.ble_handler.advertise(advertising_payload(name=self.name, services=[_UART_UUID]))

    def is_connected(self):
        return self.ble_handler._connected_central >= 0

    def _on_disconnect(self, conn_handle):
        # Flush buffer
        self.read()

    def write(self, data):
        """
        Write uart data to remote. This is a blocking call.
        """
        if self.is_connected():
            try:
                for i in range(0, len(data), MAX_NOTIFY):
                    self.ble_handler.notify(data[i:i+MAX_NOTIFY], val_handle=self._handle_tx)
                    sleep_ms(10)
            except Exception as e:
                print("Error writing:", e, data, type(data))


class UARTCentral(BleUARTBase):
    # """Class to connect to single BLE Peripheral as a Central

    # Instantiate more 'centrals' with the same ble handler to connect to
    # multiple peripherals. Things will probably break if you instantiate
    # multiple ble handlers. (EALREADY)

    # """
    def __init__(self, ble_handler: BLEHandler = None, additive_buffer=True):
        super().__init__(additive_buffer)

        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler

        self._on_disconnect()

    def _on_disconnect(self):
        # The on_disconnect callback is linked to our conn_handle
        # in _IRQ_PERIPHERAL_DISCONNECT.
        # so no need to check which conn handle it was.
        # Reset up all properties
        self._conn_handle = None
        self._periph_name = None
        self._tx_handle = 9 # None
        self._rx_handle = 12 # None
        self.writing = False
        self.reading = False

    def _on_write_done(self, value_handle, status):
        # After writing to a server, this is called when writing is done.
        # Status = 0 when the write was succesful.
        # Value handle is 65555 something, not the rx_handle. Strange.
        self.writing = False

    def connect(self, name="robot"):
        """
        Search for and connect to a peripheral with a given name.

        :param name: The name of the peripheral to connect to
        :type name: str
        """
        self._periph_name = name
        self._conn_handle, self._rx_handle, self._tx_handle = self.ble_handler.connect_uart(
            name,
            on_disconnect=self._on_disconnect,
            on_notify=self._on_rx,
            on_write_done=self._on_write_done
            ) # Blocks until timeout or device with the right name found
        return self.is_connected()

    def is_connected(self):
        return self._conn_handle is not None

    def disconnect(self):
        if self.is_connected():
            self.ble_handler._ble.gap_disconnect(self._conn_handle)

    def write(self, data):
        """
        Write uart data to remote. This is a blocking call and will wait until writing is done.

        :param data: The data to write to the peripheral
        :type data: bytes
        """
        if self.is_connected():
            try:
                # Chop data in mtu-sizes packages
                for i in range(0,len(data),self.ble_handler.mtu):
                    tries = 0
                    while tries < 50:
                        if not self.writing: # Only send when writing is done
                            self.writing = True
                            partial = data[i:i+self.ble_handler.mtu]
                            self.ble_handler.uart_write(
                                partial,
                                self._conn_handle,
                                self._rx_handle,
                                response=True)
                            break
                        else:
                            # Wait some more until writing is done.
                            tries += 1
                            sleep_ms(5)

            except Exception as e:
                print("Error writing:", partial, type(partial), len(partial), e)

    def fast_write(self, data):
        """ 
        Write to server/peripheral as fast as possible. Non-blocking.
        - Data is truncated to mtu
        - No pause after writing. Writing too often can crash the ble stack. Be careful

        :param data: The data to write to the peripheral
        :type data: bytes
        """
        if self.is_connected():
            try:
                self.ble_handler.uart_write(
                    data[:self.ble_handler.mtu],
                    self._conn_handle,
                    self._rx_handle,
                    response=False)

            except Exception as e:
                print("Error writing:", e, data)


class RCReceiver(UARTPeripheral):
    """
    Class for an Remote Control Receiver. It reads and processes gamepad or remote control data.
    It will advertise as the given name.

    :param name: The name of this peripheral to advertise as. Default: "robot"
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    """
    def __init__(self, **kwargs):
        super().__init__(additive_buffer=False, **kwargs)
        self.read_buffer = bytearray(struct.calcsize("bbbbBBhhB"))

    def button_pressed(self, button):
        """
        Returns True if the given button is pressed on the remote control.

        :param button: The button number to check. 1-8
        :type button: int
        """
        if 0 < button < 9:
            return self.controller_state(BUTTONS) & 1 << button-1
        else:
            return False

    def controller_state(self, *indices):
        """
        Returns the controller state as a list of 9 integers: 
        [left_stick_x, left_stick_y, right_stick_x, right_stick_y, left_trigger, 
        right_trigger, left_setting, right_setting, buttons]

        :param indices: The items of the selection of controller states to return. 
            If omitted, the whole list is returned. Use these constants: 
            `L_STICK_HOR, L_STICK_VER, R_STICK_HOR, R_STICK_VER, L_TRIGGER, R_TRIGGER, 
            SETTING1, SETTING2, BUTTONS`
        
        :type indices: int

        Use the controller state L_STICK indices to get only left stick values::

            left_stick_x, left_stick_y, = rc.controller_state(L_STICK_HOR, L_STICK_VER)

        """
        try:
            controller_state = struct.unpack("bbbbBBhhB", self.read_buffer)
        except:
            controller_state = [0]*9
        if indices:
            if len(indices) == 1:
                return controller_state[indices[0]]
            else:
                return [controller_state[i] for i in indices]
        else:
            return controller_state


class RCTransmitter(UARTCentral):
    """
    Class for a Remote control transmitter. It sends gamepad or remote control data to a receiver.

    :param name: The name of the peripheral to search for and connect to. Default: "robot"
    :type name: str
    :param ble_handler: A BLEHandler instance. If None, a new one will be created.
    :type ble_handler: BLEHandler
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # An empty 9-item list. Order is important.
        self.controller_state = [0]*9
        self.last_write = 0

    @staticmethod
    def clamp_int(n, floor=-100, ceiling=100):
        return max(min(round(n), ceiling), floor)

    def set_button(self, num, pressed):
        """
        Set a button to pressed or not pressed.

        :param num: The button number to set. 1-8
        :type num: int
        :param pressed: True or False
        :type pressed: bool
        """
        if 0 < num < 9:
            bitmask = 0b1 << (num-1)
            if pressed:
                self.controller_state[BUTTONS] |= bitmask
            else:
                self.controller_state[BUTTONS] &= ~bitmask

    def set_stick(self, stick, value):
        """
        Set a stick value. Value should be between -100 and 100.

        :param stick: The stick to set. Use these constants: L_STICK_HOR, L_STICK_VER, R_STICK_HOR, R_STICK_VER
        :type stick: int
        :param value: The value to set. Should be between -100 and 100.
        :type value: int
        """
        self.controller_state[stick] = self.clamp_int(value)

    def set_trigger(self, trig, value):
        """
        Set a gamepad shoulder trigger value. Value should be between 0 and 200.

        :param trig: The trigger to set. Use these constants: L_TRIGGER, R_TRIGGER
        :type trig: int
        :param value: The value to set. Should be between 0 and 200.
        :type value: int
        """
        self.controller_state[trig] = self.clamp_int(value,0,200)

    def set_setting(self, setting, value):
        """
        Set a parameter dial setting.

        :param setting: The setting to set. Use these constants: SETTING1, SETTING2
        :type setting: int
        :param value: The value to set. Should be between -32768 and 32767.
        :type value: int
        """
        self.controller_state[setting] = self.clamp_int(value, -2**15, 2**15)

    def transmit(self):
        """
        Send the controller state to the receiver.
        This call will wait if you write again within 15ms.
        """
        # Don't send too often.
        while ticks_diff(ticks_ms(), self.last_write) < 15:
            sleep_ms(1)
        value = struct.pack("bbbbBBhhB", *self.controller_state)
        self.fast_write(value)
        self.last_write = ticks_ms()
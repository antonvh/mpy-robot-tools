## TODO
## Fix occasional packet loss on very large notify payloads:
## Maybe notify size or delay
## Write blog post about ble and uart and the misery.
## Improve docs and examples.
## Create SerialTalk example.

import struct
from utime import sleep_ms
from micropython import const, schedule
import ubluetooth

TARGET_MTU = const(184) # Try to negotiate this packet size for UART
MAX_NOTIFY = const(100) # Somehow notify with the full mtu is unstable. Memory issue?

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

_NOTIFY_ENABLE = const(1)
_INDICATE_ENABLE = const(2)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# Initialize constants based on the running device
if 'FLAG_INDICATE' in dir(ubluetooth):
    # We're on MINDSTORMS Robot Inventor or ESP32
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
    _IRQ_GATTC_READ_DONE = 16
    _IRQ_MTU_EXCHANGED = 21
else:
    # We're probably on SPIKE Prime
    _IRQ_GATTS_WRITE = 1 << 2
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
    _IRQ_GATTC_READ_DONE = 1 << 15
    _IRQ_MTU_EXCHANGED = 1 << 20



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


_UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_UUID = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_LEGO_SERVICE_UUID = ubluetooth.UUID("00001623-1212-EFDE-1623-785FEABCD123")
_LEGO_SERVICE_CHAR = ubluetooth.UUID("00001624-1212-EFDE-1623-785FEABCD123")
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


def _advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    # Generate advertising payload.

    # Args:
    #     limited_disc (bool): Limited .... . Default value: ``False``.
    #     br_edr (bool): B..... . Default value: ``False`.
    #     name (str): Name ..... . Default value: ``None`.
    #     services (list): List of services ...Default value: ``None`.
    #     appearance (int): .... . Default value: ``False``.

    # Returns:
    #     An array of bytes with the specified payload.

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
    # Decode particular fields from the payload.

    # Args:
    #     payload (bytearray): Payload of the message.
    #     adv_type (?): Type of the field to decode.

    # Returns:
    #     An array with the decoded fields.

    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2: i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def _decode_name(payload):
    # Decode payload name .

    #     Args:
    #         payload (bytearray): Payload of the message.

    #     Returns:
    #         A string with the name or the payload or the empty string.

    n = _decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], "utf-8") if n else ""


def _decode_services(payload):
    # Decode service ids.

    #         Args:
    #             payload (bytearray): Payload of the message.

    #         Returns:
    #             An array with the `ids` of the available services.

    services = []
    for u in _decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(ubluetooth.UUID(struct.unpack("<h", u)[0]))
    for u in _decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(ubluetooth.UUID(struct.unpack("<d", u)[0]))
    for u in _decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(ubluetooth.UUID(u))
    return services


class BLEHandler:
    """Basic Bluetooth Low Energy class that can be a central or peripheral or both.
    The central always connects to a peripheral. The Peripheral just advertises.
    
        Args:
            debug (bool): Keep a log of events in the log property
            WARNING: Debug log is kept in memory. Long transactions will lead to memory errors!

    """
    def __init__(self, debug=False):
        self._ble = ubluetooth.BLE()
        self._ble.config(rxbuf=TARGET_MTU)
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()
        self.debug = debug

    def _reset(self):
        self._connected_centrals = set()
        self._scan_result_callback = None
        self._scan_done_callback = None
        self._write_done_callbacks = {}
        self._conn_callback = None
        self._disconn_callbacks = {}
        self._central_conn_callback = None# Used when centrals connect
        self._central_disconn_callback = None# Used when centrals disconnect
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
        self.log = ""

    def info(self, *messages):
        if self.debug:
            self.log += str(messages) + "\n"
            # print(*messages) # This is too slow and crashes the process.

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            name = _decode_name(adv_data) or "?"
            services = _decode_services(adv_data)
            self.info("Found: ", name, "with services:", services)
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
            print("New connection", conn_handle)
            self._connected_centrals.add(conn_handle)
            if self._central_conn_callback:
                self._central_conn_callback(*data)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("Disconnected", conn_handle)
            if conn_handle in self._connected_centrals:
                self._connected_centrals.remove(conn_handle)
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

    def discover_characteristics(self, args):
        self._ble.gattc_discover_characteristics(*args)

    def advertise(self, payload, interval_us=100000):
        print("Started advertising")
        self._ble.gap_advertise(interval_us, adv_data=payload)

    def on_write(self, value_handle, callback):
        self._write_callbacks[value_handle] = callback

    def on_write_done(self, conn_handle, callback):
        self._write_done_callbacks[conn_handle] = callback

    def notify(self, data, val_handle, conn_handle=None):
        # Notify all connected centrals interested in the handle
        if conn_handle is not None:
            self._ble.gatts_notify(conn_handle, val_handle, data)
        else:
            for conn_handle in self._connected_centrals:
                self._ble.gatts_notify(conn_handle, val_handle, data)

    def register_uart_service(self, on_write=None, on_connect=None, on_disconnect=None):
        ((handle_tx, handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        self.on_write(handle_rx, on_write)
        self._central_conn_callback = on_connect
        self._central_disconn_callback = on_disconnect

        # Characteristics and descriptors have a default maximum size of 20 bytes.
        # Anything written to them by a client will be truncated to this length.
        # However, any local write will increase the maximum size, so if you want
        # to allow larger writes from a client to a given characteristic,
        # use gatts_write after registration.

        # Increase buffer size to fit MTU
        self._ble.gatts_set_buffer(handle_rx, TARGET_MTU)
        # self._ble.gatts_set_buffer(handle_tx, 200) #tx is handle with notify. No buffer.

        # Stretch buffer
        self._ble.gatts_write(handle_rx, bytes(TARGET_MTU))
        # self._ble.gatts_write(handle_tx, bytes(200))

        # Flush
        _ = self._ble.gatts_read(handle_rx)
        # _ = self._ble.gatts_read(handle_tx)
        return handle_tx, handle_rx

    # Find a device advertising the uart service.
    def scan(self):
        self._ble.gap_scan(20000, 30000, 30000)

    def stop_scan(self):
        self._ble.gap_scan(None)

    def connect_uart(self, name="robot", on_disconnect=None, on_notify=None, on_write_done=None, time_out=10):
        """ Connect to a BLE Peripheral that advertises with a certain name
        This method is meant for BLE Centrals

        Args:
            name (str): Device name to look for
            on_disconnect (def): Method to call when any side disconnects
            on_notify (def): Method to call when Peripheral sends notify data.
            time_out (int): Number of seconds to wait for a connection. 
        Returns:

        """
        
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
        for i in range(time_out):
            print("Connecting to UART Peripheral:", name)
            sleep_ms(1000)
            if not self.connecting_uart:
                break
        if self._conn_handle:
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
        self.connecting_lego = True
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._lego_value_handle = None
        self._addr_type = None
        self._addr = None
        self.scan()
        for i in range(time_out):
            print("Connecting to a LEGO Smart Hub...")
            sleep_ms(1000)
            if not self.connecting_lego:
                break
        self.connecting_lego = False
        return self._conn_handle

    def uart_write(self, value, conn_handle, rx_handle=12, response=False):
        self._ble.gattc_write(conn_handle, rx_handle, value, 1 if response else 0)
        self.info("GATTC Written ", value)

    def read(self, conn_handle, value_handle):
        self._read_data[(value_handle << 12) + conn_handle] = b''
        try:
            self._ble.gattc_read(conn_handle, value_handle)
        except Exception as e:
            print("gattc_read failed", e)
        for i in range(100):
            result = self._read_data[(value_handle << 12) + conn_handle]
            if result:
                return result
            else:
                sleep_ms(10)

    def lego_write(self, value, conn_handle=None, response=False):
        if not conn_handle: conn_handle = self._conn_handle
        if self._lego_value_handle and conn_handle is not None:
            self._ble.gattc_write(conn_handle, self._lego_value_handle, value, 1 if response else 0)
            self.info("GATTC Written ", value)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type, addr):
        self._ble.gap_connect(addr_type, addr)

    def disconnect(self, conn_handle):
        self._ble.gap_disconnect(conn_handle)

    def enable_notify(self, conn_handle, desc_handle, callback=None):
        self._ble.gattc_write(conn_handle, desc_handle, struct.pack('<h', _NOTIFY_ENABLE), 0)
        if callback:
            self._notify_callbacks[conn_handle] = callback


class BleUARTBase:
    """Base class with a buffer for UART methods any() and read()

    Args:
        Buffered (bool): Add to the buffer or overwrite the buffer 
            when new data arrives. Default: True

    """
    # TODO: Implement more the UART methods.

    def __init__(self, additive_buffer=True):
        self.additive_buffer = additive_buffer
        self.read_buffer = bytearray()
        
    def _on_rx(self, data):
        if self.additive_buffer:
            self.read_buffer += data
        else:
            self.read_buffer = data

    def any(self):
        return len(self.read_buffer)

    def read(self, n=-1):
        bufsize = len(self.read_buffer)
        if n < 0 or n > bufsize:
            n = bufsize
        data = self.read_buffer[:n]
        self.read_buffer = self.read_buffer[n:]
        return data

    def readline(self):
        data = bytearray()
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
        return data


class UARTPeripheral(BleUARTBase):
    """
    Class for a Nordic UART BLE server/peripheral.
    It will advertise as the given name and populate the UART services and characteristics
    """

    def __init__(self, name="robot", ble_handler: BLEHandler = None, additive_buffer=True):
        super().__init__(additive_buffer)
        self.name = name
        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler

        self._handle_tx, self._handle_rx = self.ble_handler.register_uart_service(
            on_write = self._on_rx, 
            on_connect = self._on_connect,
            on_disconnect = self._on_disconnect
            )
        
        self.connected_centrals = set() # Sets cannot have duplicate items.
        self.ble_handler.advertise(_advertising_payload(name=self.name, services=[_UART_UUID]))

    def is_connected(self):
        return len(self.connected_centrals)

    def _on_disconnect(self, conn_handle):
        if conn_handle in self.connected_centrals:
            self.connected_centrals.remove(conn_handle)
        # Flush buffer
        self.read()
        # Print debug history
        if self.ble_handler.log:
            print(self.ble_handler.log)
            self.ble_handler.log = ""

    def _on_connect(self, conn_handle, addr_type, addr):
        self.connected_centrals.add(conn_handle)

    def write(self, data):
        # Notify central of new data.
        if self.is_connected():
            try:
                for c in self.connected_centrals:
                    for i in range(0, len(data), MAX_NOTIFY):
                        self.ble_handler.notify(data[i:i+MAX_NOTIFY], val_handle=self._handle_tx, conn_handle=c)
                        sleep_ms(10)
            except Exception as e:
                print("Error writing:", e, data, type(data))


class UARTCentral(BleUARTBase):
    """Class to connect to single BLE Peripheral as a Central

    Instantiate more 'centrals' with the same ble handler to connect to
    multiple peripherals. Things will probably break if you instantiate
    multiple ble handlers. (EALREADY)

    """
    def __init__(self, ble_handler: BLEHandler = None, additive_buffer=True):
        super().__init__(additive_buffer)

        if ble_handler is None:
            ble_handler = BLEHandler()
        self.ble_handler = ble_handler
        
        self._on_disconnect()

    def __del__(self):
        self.disconnect()

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
            self.ble_handler.disconnect(self._conn_handle)

    def write(self, data):
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
        """ Write to server/peripheral as fast as possible
        - Data is truncated to mtu
        - No pause after writing. Writing too often can crash the ble stack. Be careful

        Args:
            data (str or bytes): Payload to transmit
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

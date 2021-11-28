if __name__ == '__main__':
    from micropython import const, alloc_emergency_exception_buf, schedule
    from time import sleep_ms
    import ubluetooth
    import ubinascii
    import struct
    import hub
    from hub import display, Image

    _CONNECT_IMG_1 = Image("00000:09000:09000:09000:00000")
    _CONNECT_IMG_2 = Image("00000:00900:00900:00900:00000")
    _CONNECT_IMG_3 = Image("00000:00090:00090:00090:00000")

    _COMPLETE_IMG = Image("00000:05550:05950:05550:00000")
    _CONNECT_CHILDREN_SEARCH_IMG = Image("55000:50000:50000:50000:55000")
    _CONNECT_CHILDREN_FOUND_IMG = Image("99000:90000:90000:90000:99000")
    _CONNECT_ANIMATION_C_S = [_CONNECT_IMG_1+_CONNECT_CHILDREN_SEARCH_IMG,
                            _CONNECT_IMG_2+_CONNECT_CHILDREN_SEARCH_IMG,
                            _CONNECT_IMG_3+_CONNECT_CHILDREN_SEARCH_IMG]

class ble_handler:
    """  Class to handle BLE devices
    """

    def __init__(self):
        """
        Create instance of ble_handler
        """
        # constants

        if hub.info()['product_variant'] == 1:
            self.__IRQ_SCAN_RESULT = const(5)
            self.__IRQ_SCAN_COMPLETE = const(6)
            self.__IRQ_PERIPHERAL_CONNECT = const(7)
            self.__IRQ_PERIPHERAL_DISCONNECT = const(8)
            self.__IRQ_GATTC_SERVICE_RESULT = const(9)
            self.__IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
            self.__IRQ_GATTC_READ_RESULT = const(15)
            self.__IRQ_GATTC_NOTIFY = const(18)
        else:
            self.__IRQ_SCAN_RESULT = const(1 << 4)
            self.__IRQ_SCAN_COMPLETE = const(1 << 5)
            self.__IRQ_PERIPHERAL_CONNECT = const(1 << 6)
            self.__IRQ_PERIPHERAL_DISCONNECT = const(1 << 7)
            self.__IRQ_GATTC_SERVICE_RESULT = const(1 << 8)
            self.__IRQ_GATTC_CHARACTERISTIC_RESULT = const(1 << 9)
            self.__IRQ_GATTC_READ_RESULT = const(1 << 11)
            self.__IRQ_GATTC_NOTIFY = const(1 << 13)

        self.__LEGO_SERVICE_UUID = ubluetooth.UUID("00001623-1212-EFDE-1623-785FEABCD123")
        self.__LEGO_SERVICE_CHAR = ubluetooth.UUID("00001624-1212-EFDE-1623-785FEABCD123")

        # class specific
        self.__ble = ubluetooth.BLE()
        self.__ble.active(True)
        self.__ble.irq(handler=self.__irq)
        self.__decoder = _Decoder()
        self.__reset()
        self.debug = False

        # callbacks
        self.__scan_callback = None
        self.__read_callback = None
        self.__notify_callback = None
        self.__connected_callback = None
        self.__disconnected_callback = None

    def __reset(self):
        """ reset all necessary variables
        """
        # cached data
        self.__addr = None
        self.__addr_type = None
        self.__adv_type = None
        self.__services = None
        self.__man_data = None
        self.__name = None
        self.__conn_handle = None
        self.__value_handle = None

        # reserved callbacks
        self.__scan_callback = None
        self.__read_callback = None
        self.__notify_callback = None
        self.__connected_callback = None
        self.__disconnected_callback = None

    def __log(self, *args):
        """ log function if debug flag is set

        :param args: arguments to log
        :returns: nothing
        """
        if not self.debug:
            return
        print(args)

    def scan_start(self, timeout, callback):
        """ start scanning for devices

        :param timeout: timeout in ms
        :param callback: callback function, contains scan data
        :returns: nothing
        """
        self.__log("start scanning...")
        self.__update_animation()
        self.__scan_callback = callback
        self.__ble.gap_scan(timeout, 30000, 30000)

    def scan_stop(self):
        """ stop scanning for devices

        :returns: nothing
        """
        self.__ble.gap_scan(None)

    def write(self, data, adv_value=None):
        """ write data to gatt client

        :param data: data to write
        :param adv_value: advanced value to write
        :returns: nothing
        """
        
        if not self.__is_connected():
            return
        if adv_value:
            self.__ble.gattc_write(self.__conn_handle, adv_value, data)
        else:
            self.__ble.gattc_write(self.__conn_handle, self.__value_handle, data)

    def read(self, callback):
        """ read data from gatt client

        :param callback: callback function, contains readed data
        :returns: nothing
        """
        if not self.__is_connected():
            return
        self.__read_callback = callback
        self.__ble.gattc_read(self.__conn_handle, self.__value_handle)

    def connect(self, addr_type, addr):
        """ connect to a ble device

        :param addr_type: the address type of the device
        :param addr: the devices mac a binary
        :returns: nothing
        """
        self.__ble.gap_connect(addr_type, addr)

    def disconnect(self):
        """ disconnect from a ble device

        :returns: nothing
        """
        if not self.__is_connected():
            return
        self.__ble.gap_disconnect(self.__conn_handle)

    def on_notify(self, callback):
        """ create a callback for on notification actions

        :param callback: callback function, contains notify data
        :returns: nothing
        """
        self.__notify_callback = callback

    def on_connect(self, callback):
        """ create a callback for on connect actions

        :param callback: callback function
        :returns: nothing
        """
        self.__connected_callback = callback

    def on_disconnect(self, callback):
        """ create a callback for on disconnect actions

        :param callback: callback function
        :returns: nothing
        """
        self.__disconnected_callback = callback
        
    def is_connected(self):
        """ check if hub is connected
        
        :returns: nothing
        """
        return self.__is_connected()

    """
    private functions
    -----------------
    """

    def __is_connected(self):
        return self.__conn_handle is not None and self.__value_handle is not None

    def __irq(self, event, data):
        if event == self.__IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            self.__log("result with uuid:", self.__decoder.decode_services(adv_data))
            if self.__LEGO_SERVICE_UUID in self.__decoder.decode_services(adv_data):
                self.__addr_type = addr_type
                self.__addr = bytes(addr)
                self.__adv_type = adv_type
                self.__name = self.__decoder.decode_name(adv_data)
                self.__services = self.__decoder.decode_services(adv_data)
                self.__man_data = self.__decoder.decode_manufacturer(adv_data)
                self.scan_stop()

        elif event == self.__IRQ_SCAN_COMPLETE:
            if self.__addr:
                if self.__scan_callback:
                    self.__scan_callback(self.__addr_type, self.__addr, self.__man_data)
                self.__scan_callback = None
            else:
                self.__scan_callback(None, None, None)

        elif event == self.__IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.__conn_handle = conn_handle
            self.__ble.gattc_discover_services(self.__conn_handle)

        elif event == self.__IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, _, _ = data
            #self.__disconnected_callback()
            print("disconnected")
            if conn_handle == self.__conn_handle:
                self.__reset()
                self.__update_animation()
                self.scan_start(30000,None)

        elif event == self.__IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            if conn_handle == self.__conn_handle and uuid == self.__LEGO_SERVICE_UUID:
                sleep_ms(100)
                self.__ble.gattc_discover_characteristics(self.__conn_handle, start_handle, end_handle)

        elif event == self.__IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self.__conn_handle and uuid == self.__LEGO_SERVICE_CHAR:
                self.__value_handle = value_handle
                schedule(self.__connected_callback,1)
                schedule(self.__update_animation,1)

        elif event == self.__IRQ_GATTC_READ_RESULT:
            conn_handle, value_handle, char_data = data
            if self.__read_callback:
                self.__read_callback(char_data)

        elif event == self.__IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if self.__notify_callback:
                schedule(self.__notify_callback,notify_data)
                
    def __update_animation(self,*arg):
        if not self.__is_connected():
            display.show(_CONNECT_ANIMATION_C_S, delay=100, wait=False, loop=True)
        else:
            display.show(_COMPLETE_IMG+_CONNECT_CHILDREN_FOUND_IMG)


class _Decoder:
    """
    Class to decode BLE adv_data
    """

    def __init__(self):
        """
        create instance of _Decoder
        """
        self.__COMPANY_IDENTIFIER_CODES = {"0397": "LEGO System A/S"}

    def decode_manufacturer(self, payload):
        """
        decode manufacturer information from ble data

        :param payload: payload data to decode
        :returns: nothing
        """
        man_data = []
        n = self.__decode_field(payload, const(0xFF))
        if not n:
            return []
        company_identifier = ubinascii.hexlify(struct.pack("<h", *struct.unpack(">h", n[0])))
        company_name = self.__COMPANY_IDENTIFIER_CODES.get(company_identifier.decode(), "?")
        company_data = n[0][2:]
        man_data.append(company_identifier.decode())
        man_data.append(company_name)
        man_data.append(company_data)
        return man_data

    def decode_name(self, payload):
        """
        decode name information from ble data

        :param payload: payload data to decode
        :returns: nothing
        """
        n = self.__decode_field(payload, const(0x09))
        return str(n[0], "utf-8") if n else "parsing failed!"

    def decode_services(self, payload):
        """
        decode services information from ble data

        :param payload: payload data to decode
        :returns: nothing
        """
        services = []
        for u in self.__decode_field(payload, const(0x3)):
            services.append(ubluetooth.UUID(struct.unpack("<h", u)[0]))
        for u in self.__decode_field(payload, const(0x5)):
            services.append(ubluetooth.UUID(struct.unpack("<d", u)[0]))
        for u in self.__decode_field(payload, const(0x7)):
            services.append(ubluetooth.UUID(u))
        return services

    """
    private functions
    -----------------
    """

    def __decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2: i + payload[i] + 1])
            i += 1 + payload[i]
        return result   
    
class Led:
    """
    Class to control build in LED
    """
    
    def __init__(self,hub,port):
        """ 
        Set LED color
        
        :param color: color index
        :type color: integer
        """
        self.__color = 3
        self.__port = port
        self.__hub = hub        
        
    def __call__(self,color):
        """
        Led(color)
        On call method to set LED color

        :param color: color index
        :type color: integer
        """
        if color != self.__color:
            self.__color = color
            self.__set_led_color()
        
    """
    private functions
    -----------------
    """
    def __set_led_color(self):
        """ Send message over BLE to change LED color """
        
        color = self.__hub.__create_message([0x08, 0x00, 0x81, self.__port, 0x11, 0x51, 0x00, self.__color])
        self.__hub.__handler.write(color)

class Button:
    """ Class to control a button """

    def __init__(self):
        """ Create a instance of a single button """

        # button state
        self.__is_pressed = False
        self.__was_pressed = False
        self.__presses = 0

    def is_pressed(self):
        """
        check if button is pressed

        :returns: True if button is pressed; False if button is not pressed
        """

        return self.__is_pressed

    def was_pressed(self):
        """
        check if button was pressed since last call 

        :returns: True if button was pressed since last call; False if button was not pressed since last call
        """
        value = self.__was_pressed
        self.__was_pressed = False
        return value

    def presses(self):
        """
        Number of presses since last call

        :returns: integer value of number of presses since last call
        """ 
        value = self.__presses
        self.__presses = 0
        return value

    """
    private functions
    -----------------
    """

    def __update(self,pressed):
        """ update button state variables

        :param pressed: boolean True if update initiated by a press on the button; False if update initiated by a release of a button
        :returns: nothing
        """

        if pressed:
            self.__presses += 1
            self.__is_pressed = True
        else:
            if self.__is_pressed:
                self.__was_pressed = True
            self.__is_pressed = False           

class RemoteButton:
    """ Class to control button on a PoweredUP Remote """

    def __init__(self,hub,port):
        """
        Create a instance of a remote button
        """

        self.__port = port
        self.__hub = hub

        self.plus = Button()
        self.red  = Button()
        self.min  = Button()
        
        SUBSCRIBE_REMOTE_BUTTON = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        
        self.__hub.__add_connect_message(SUBSCRIBE_REMOTE_BUTTON)
        
        self.__hub.__update_measurement[self.__port] = self.__update

    """
    private functions
    -----------------
    """  

    def __update(self,payload):
        """ update button state variables

        :param event:  byte refering to button event
        :returns: nothing
        """

        event = payload[0]
        if event == 0x01:
            self.plus.__update(True)
        elif event == 0x7F:
            self.red.__update(True)
        elif event == 0xFF:
            self.min.__update(True)
        elif event == 0x00:
            self.plus.__update(False)
            self.red.__update(False)
            self.min.__update(False)

class Motion:
    """ Class to handle motion sensor in PoweredUP hub

    Supported on: |technic_hub|
    """

    def __init__(self, hub, port_acc = None, port_gyro = None, port_tilt = None):
        """ Create a instance of motion sensor """
        self.__hub = hub
        
        self.__port_acc = port_acc
        self.__port_gyro = port_gyro
        self.__port_tilt = port_tilt
        
        self.__acc = [0, 0, 0]
        self.__gyro = [0, 0, 0]
        self.__tilt = [0, 0, 0]
        
        SUBSCRIBE_ACCELEROMETER = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port_acc, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        SUBSCRIBE_GYRO = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port_gyro, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        SUBSCRIBE_TILT = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port_tilt, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        
        self.__hub.__add_connect_message(SUBSCRIBE_ACCELEROMETER)
        self.__hub.__add_connect_message(SUBSCRIBE_GYRO)
        self.__hub.__add_connect_message(SUBSCRIBE_TILT)
        
        self.__hub.__update_measurement[self.__port_acc] = self.__update_acc
        self.__hub.__update_measurement[self.__port_gyro] = self.__update_gyro
        self.__hub.__update_measurement[self.__port_tilt] = self.__update_tilt

    def accelerometer(self):
        """ Measure acceleration around three axis 

        :return: accleration around x,y,z axis
        :rtype: tuple
        """
        
        return self.__acc

    def gyroscope(self):
        """ Measure gyro rates around three axis 

        :returns: gyro rates around x,y,z axis
        :rtype: tuple
        """
        return self.__gyro

    def yaw_pitch_roll(self):
        """ Measure yaw pitch roll angles  

        :return: yaw pitch roll angle
        :rtype: tuple
        """
        
        return self.__tilt
    
    """
    private functions
    -----------------
    """
    def __update_acc(self,payload):
        """ Update accelerations """
        self.__acc = struct.unpack("%sh" % 3, payload)

    def __update_gyro(self,payload):
        """ Update gyro rates"""
        self.__gyro = struct.unpack("%sh" % 3, payload)
            
    def __update_tilt(self,payload):
        """ Update tilt angles """
        self.__tilt = struct.unpack("%sh" % 3, payload)
        
class X():
    """ Class to control a PoweredUp device connect to a single port """
    
    def __init__(self,hub,port):
        """ Create instance of a single port """
        self.device = Device(hub, port)
        self.motor = Motor(hub,port,self.device)
    
            
class Port():
    """ Class to control PoweredUp devices connected to the physical ports """   
   
    def __init__(self,hub,ports):
        """ Create a instance of Port """
        
        self.__hub = hub
        
        for Y, port in ports.items():
            setattr(self,Y, X(self.__hub, port))
    
class Device:
    """ Class to control PoweredUp devices connected to a physical port

    Supported on: |technic_hub| |city_hub| 
    """
    
    def __init__(self,hub,port):
        """ Create a instance of device """
        self.__hub = hub
        self.__port = port
        self.__mode = 0
        self.__no_data_sets = None
        self.__data_set_type = None
        self.__value = (0, )
        
        SUBSCRIBE_MODE_0 = self.__hub.__create_message([0x0A,0x00,0x41, self.__port, self.__mode, 0x01, 0x00, 0x00, 0x00, 0x01])
        GET_MODE_INFO = self.__hub.__create_message([0x06, 0x00, 0x22, self.__port, self.__mode, 0x80])
        
        self.__hub.__update_measurement[self.__port] = self.__update
        self.__hub.__update_mode_info[self.__port] = self.__update_mode_info
        
        self.__hub.__add_connect_message(SUBSCRIBE_MODE_0)
        self.__hub.__add_connect_message(GET_MODE_INFO)
    
    def mode(self, mode, *data):
        """ Set the mode of the sensor

        :param mode: new mode
        :type mode: byte
        
        :param *data: optional data to be send allong with mode, e.g., to turn on LEDs of a sensor
        :type *data: bytearray
        """
        if mode != self.__mode:
            self.__mode = mode
            set_mode = self.__hub.__create_message([0x0A,0x00,0x41, self.__port, mode, 0x01, 0x00, 0x00, 0x00, 0x01])
            self.__hub.__handler.write(set_mode)
            sleep_ms(100)
            request_mode_info = self.__hub.__create_message([0x06, 0x00, 0x22, self.__port, mode, 0x80])
            self.__hub.__handler.write(request_mode_info)
            sleep_ms(100)
        if data:
            send_data = self.__hub.__create_message([7+len(data), 0x00, 0x81, self.__port, 0x00, 0x51, mode] + data[0])
            self.__hub.__handler.write(send_data)
            sleep_ms(100)
        pass

    def get(self):
        """ Get measurement of the sensor corresponding to the active mode

        :returns: measurement
        :rtype: tuple
        """

        return self.__value
    
    """
    private functions
    -----------------
    """
    def __update(self,payload):
        if self.__data_set_type == 0x00:
            message = struct.unpack("%sb" % len(payload), payload)
            self.__value = message[:self.__no_data_sets]
        elif self.__data_set_type == 0x01:
            message = struct.unpack("%sh" % (len(payload)//2), payload)
            self.__value = message[:self.__no_data_sets]
        elif self.__data_set_type == 0x02:
            message = struct.unpack("%si" % (len(payload)//4), payload)
            self.__value = message[:self.__no_data_sets]
        
    def __update_mode_info(self, payload):
        if self.__mode == payload[0] and payload[1]==0x80:
            self.__no_data_sets = payload[2]
            self.__data_set_type = payload[3]
    
class Motor:
    """ Class to control PoweredUp motors
    
    Supported on: |technic_hub| |city_hub|
    """
    
    def __init__(self, hub, port, device):
        self.__hub = hub
        self.__port = port
        self.__device = device
        
    def mode(self, mode):
        """ Set the mode of the motor, this mainly affects the measurement output

        :param mode: new mode
        :type mode: byte
        """
        self.__device.mode(mode)
    
    def get(self):
        """ Get measurement of the motor corresponding to the active mode

        :returns: measurement
        :rtype: tuple
        """
        return self.__device.get()

    def pwm(self,power):
        """ Set motor power

        :param power: in range [-100,..., 100]
        :type power: int
        """
        set_power = self.__hub.__create_message([0x06, 0x00, 0x81, self.__port, 0x11, 0x51, 0x00, power])
        self.__hub.__handler.write(set_power)

    def run_at_speed(self,speed, max_power=100, acceleration=100, deceleration=100):
        """ Start motor at given speed

        :param speed: a percentage off the maximum speed of the motor in the range [-100,..., 100] 
        :type speed: int
        
        :param max_power: maximum power that can be used by the motor
        :type max_power: int
        
        :param acceleration: the duration time for an acceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an acceleration time of 300 ms from 40% to 70%
        :type acceleration: int
        
        :param deceleration: the duration time for a deceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an deceleration time of 300 ms from 70% to 40%
        :type deceleration: int
        """
        set_speed = self.__hub.__create_message([0x09, 0x00, 0x81, self.__port, 0x11, 0x07, speed, max_power, 0x00])
        self.__hub.__handler.write(set_speed)

    def run_for_time(self,time, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        """ Rotate motor for a given time

        :param time: time in milliseconds
        :type speed: int

        :param speed: a percentage off the maximum speed of the motor in the range [-100,..., 100] 
        :type speed: int
        
        :param max_power: maximum power that can be used by the motor
        :type max_power: int
        
        :param acceleration: the duration time for an acceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an acceleration time of 300 ms from 40% to 70%
        :type acceleration: int
        
        :param deceleration: the duration time for a deceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an deceleration time of 300 ms from 70% to 40%
        :type deceleration: int
        
        :param stop_action: action performed after the given time: ``float = 0``, ``brake = 1``, ``hold = 2``
        :type stop_action: int
        """
        time_bits = struct.unpack("<BB", struct.pack("<H", time))
        set_speed_time = self.__hub.__create_message([0x0B, 0x00, 0x81, self.__port, 0x11, 0x09, time_bits[0], time_bits[1], speed, max_power, 0x00])
        self.__hub.__handler.write(set_speed_time)

    def run_for_degrees(self,degrees, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        """ Rotate motor for a given number of degrees relative to current position

        :param degrees: relative degrees
        :type degress: int

        :param speed: a percentage off the maximum speed of the motor in the range [-100,..., 100] 
        :type speed: int
        
        :param max_power: maximum power that can be used by the motor
        :type max_power: int
        
        :param acceleration: the duration time for an acceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an acceleration time of 300 ms from 40% to 70%
        :type acceleration: int
        
        :param deceleration: the duration time for a deceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an deceleration time of 300 ms from 70% to 40%
        :type deceleration: int
        
        :param stop_action: action performed after the given time: ``float = 0``, ``brake = 1``, ``hold = 2``
        :type stop_action: int
        """
        degree_bits = struct.unpack("<BBBB", struct.pack("<i", degrees))
        run_degree = self.__hub.__create_message([0x0D, 0x00, 0x81, self.__port, 0x11, 0x0B, degree_bits[0], degree_bits[1], degree_bits[2], degree_bits[3], speed, max_power, 0x7E])
        self.__hub.__handler.write(run_degree)

    def run_to_position(self,degrees, speed=50, max_power=100, acceleration=100, deceleration=100, stop_action=0):
        """ Rotate motor for a given number of degrees relative to current position

        :param degrees: relative degrees
        :type degress: int

        :param speed: a percentage off the maximum speed of the motor in the range [-100,..., 100] 
        :type speed: int
        
        :param max_power: maximum power that can be used by the motor
        :type max_power: int
        
        :param acceleration: the duration time for an acceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an acceleration time of 300 ms from 40% to 70%
        :type acceleration: int
        
        :param deceleration: the duration time for a deceleration from 0 to 100%. i.e. a time set to 1000 ms. should give an deceleration time of 300 ms from 70% to 40%
        :type deceleration: int
        
        :param stop_action: action performed after the given time: ``float = 0``, ``brake = 1``, ``hold = 2``
        :type stop_action: int
        """
        degree_bits = struct.unpack("<BBBB", struct.pack("<i", degrees))
        run_degree = self.__hub.__create_message([0x0D, 0x00, 0x81, self.__port, 0x11, 0x0D, degree_bits[0], degree_bits[1], degree_bits[2], degree_bits[3], speed, max_power, 0x7E])
        self.__hub.__handler.write(run_degree)

    def float(self):
        """ Float motor from current position """
        set_power = self.__hub.__create_message([0x06, 0x00, 0x81, self.__port, 0x11, 0x51, 0x00, 0x00])
        self.__hub.__handler.write(set_power)

    def brake(self):
        """ Brake motor at current position """
        set_power = self.__hub.__create_message([0x06, 0x00, 0x81, self.__port, 0x11, 0x51, 0x00, 0x7F])
        self.__hub.__handler.write(set_power)

    def hold(self):
        """ Actively hold motor at current position """
        set_power = self.__hub.__create_message([0x06, 0x00, 0x81, self.__port, 0x11, 0x51, 0x00, 0x7F])
        self.__hub.__handler.write(set_power)

    def busy(type):
        pass
    
class Barcode:
    """ Class to handle barcode sensor

    Supported on: |mario|
    """

    def __init__(self, hub, port):
        """ Create a instance of barcode sensor """
        self.__hub = hub
        self.__port = port
        
        self.__color = 0x0138
        self.__barcode = 0
        
        SUBSCRIBE_BARCODE = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        
        self.__hub.__add_connect_message(SUBSCRIBE_BARCODE)
        
        self.__hub.__update_measurement[self.__port] = self.__update_barcode

    def get(self):
        """ Return current barcode and color

        :return: barcode, color
        :rtype: tuple
        """
        
        return (self.__barcode, self.__color,)
    
    """
    private functions
    -----------------
    """
    def __update_barcode(self,payload):
        """ Update barcode and color """
        data = struct.unpack("%sH" % 2, payload)
        if data[0] != 0xFFFF:
            self.__barcode = data[0]
        else:
            self.__barcode = None
            
        if data[1] != 0xFFFF:
            self.__color = data[1]
        else:
            self.__color = None
         
class MotionMario:
    """ Class to handle motion sensor in LEGO Mario

    Supported on: |mario|
    """

    def __init__(self, hub, port):
        """ Create a instance of gesture sensor """
        self.__hub = hub
        self.__port = port
        
        self.__value = [0,]
        self.__observed_gestures = []
        
        SUBSCRIBE_GESTURE = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01])
        
        self.__hub.__add_connect_message(SUBSCRIBE_GESTURE)
        
        self.__hub.__update_measurement[self.__port] = self.__update_gesture

    def gesture(self):
        """ Return active gesture

        :return: gesture
        :rtype: int
        """
        return self.__value[0]
    
    def was_gesture(self, gesture):
        """ Return if gesture was active since last call

        :param gesture: gesture to check
        :type gesture: int    
        :return: True if gesture was active since last call, otherwise False
        :rtype: boolean
        """
        
        check = gesture in self.__observed_gestures
        self.__observed_gestures = []
        return check
    
    """
    private functions
    -----------------
    """
    def __update_gesture(self,payload):
        """ Update gestures"""
        self.__value = struct.unpack("%sH" % 1, payload[:2])
        if self.__value[0] not in self.__observed_gestures:
            self.__observed_gestures.append(self.__value[0])

class Pants:
    """ Class to detect a LEGO Mario pants

    Supported on: |mario|
    """

    def __init__(self, hub, port):
        """ Create a instance of gesture sensor """
        self.__hub = hub
        self.__port = port
        
        self.__value = [0,]
        
        SUBSCRIBE_PANTS = self.__hub.__create_message([0x0A, 0x00, 0x41, self.__port, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01])
        
        self.__hub.__add_connect_message(SUBSCRIBE_PANTS)
        
        self.__hub.__update_measurement[self.__port] = self.__update_pants

    def get(self):
        """ Get current pants

        :return: value corresponding to a pants
        :rtype: int
        """
        return self.__value[0]

    
    """
    private functions
    -----------------
    """
    def __update_pants(self,payload):
        """ Update gestures"""
        self.__value = struct.unpack("%sB" % 1, payload)

class PUPhub:
    """ General LEGO PoweredUP hub class
    
    The methods included in this class are identical for each PoweredUP hub
    
    Replace ``PUPhub`` with
    
    * ``TechnicHub`` for |technic_hub|
    * ``CityHub`` for |city_hub|
    * ``Remote`` for |remote|
    * ``Mario`` for |mario|
    
    """
    
    def __init__(self,bt_handler):
        """ Create a instance of a general LEGO PoweredUP hub

        :param bt_handler: the bluetooth handler
        :type bt_handler: ble_handler
        """ 
        self.__handler = bt_handler
        self.__on_connect_messages = []
        self.__update_measurement={}
        self.__update_mode_info = {}
                
    def connect(self, timeout=30000, address=None):
        """ Connect to the PoweredUP hub

        :param timeout: time of scanning for devices in ms, default is 30000
        :param address: mac address of device (optional), connect to a specific device if set
        """
        if address:
            self.__address = ubinascii.unhexlify(address.replace(":", ""))
        self.__handler.debug = self.debug
        self.__handler.on_connect(callback=self.__on_connect)
        self.__handler.on_notify(callback=self.__on_notify)
        self.__handler.scan_start(timeout, callback=self.__on_scan)

        while not self.is_connected():
            pass
        
        
        for message in self.__on_connect_messages:
            self.__handler.write(message)
            sleep_ms(100)
            
        notifier = self.__create_message([0x01, 0x00])
            
        self.__handler.write(notifier, self.__notify_handler)
        sleep_ms(100)
    
    def disconnect(self):
        """ Disconnect from a PoweredUP hub """
        self.__handler.disconnect()

        
    def is_connected(self):
        """ Check if hub is connected

        :returns: True if hub is connected
        :rtype: boolean
        """
        return self.__handler.is_connected()
    
    """
    private functions
    -----------------
    """
    def __on_connect(self,*arg):
        pass
        
    def __on_scan(self, addr_type, addr, man_data):
        if not self.__address:
            if addr and man_data[2][1] == self.__HUB_ID:
                self.__handler.connect(addr_type, addr)
        else:
            if self.__address == addr and man_data[2][1] == self.__HUB_ID:
                self.__handler.connect(addr_type, addr)
                
    def __on_notify(self, data):
        header = struct.unpack("%sB" % len(data), data)
        hub = data[1]
        message_type = data[2]
        port = data[3]
        payload = data[4:]
        if message_type == 0x45:
            if port in self.__update_measurement.keys():
                self.__update_measurement[port](payload)
        elif message_type == 0x44:
            if port in self.__update_mode_info.keys():
                self.__update_mode_info[port](payload)
    
    def __add_connect_message(self,message):
        self.__on_connect_messages.append(message)
    
    def __create_message(self, byte_array):
        message = struct.pack("%sB" % len(byte_array), *byte_array)
        return message  

        
class TechnicHub(PUPhub):
    
    def __init__(self, handler):
        super().__init__(handler)
        self.debug = False
        
        # Technic Hub specifics
        self.__HUB_ID = 0x80
        self.__notify_handler = 0x0F
        
        # Hub specifics
        self.__address = None
        
        # Devices
        self.led = Led(self,0x32)
        self.motion = Motion(self,0x61, 0x62, 0x63)
        self.port = Port(self,{"A":0x00, "B":0x01, "C":0x02, "D":0x03})
        
class CityHub(PUPhub):
    
    def __init__(self, handler):
        super().__init__(handler)
        self.debug = False
        
        # Technic Hub specifics
        self.__HUB_ID = 0x41
        self.__notify_handler = 0x0F
        
        # Hub specifics
        self.__address = None
        
        # Devices
        self.led = Led(self,0x32)
        self.port = Port(self,{"A":0x00, "B":0x01})
        
class Remote(PUPhub):
    
    def __init__(self, handler):
        super().__init__(handler)
        self.debug = False
        
        # Remote specifics
        self.__HUB_ID = 0x42
        self.__notify_handler = 0x0C
        
        # Hub specifics
        self.__address = None
        
        # Devices
        self.led = Led(self, 0x34)
        self.left = RemoteButton(self, 0x00)
        self.right = RemoteButton(self, 0x01)
        
class Mario(PUPhub):
    
    def __init__(self, handler):
        super().__init__(handler)
        self.debug = False
        
        # Remote specifics
        self.__HUB_ID = 0x43
        self.__notify_handler = 14
        
        # Hub specifics
        self.__address = None
        
        # Devices
        self.motion = MotionMario(self,0x00)
        self.barcode = Barcode(self,0x01)
        self.pants = Pants(self,0x02)
        
def version():
    return "0.1.0"
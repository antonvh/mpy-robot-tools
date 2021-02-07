### Soft I2c TOF VL53L0X distance sensing on SPIKE Prime ###
### DOESN'T WORK (YET?) ###

import utime
import hub
from micropython import const
import ustruct

## Soft i2c ##
IN = 0
OUT = 1
LOW = 0
HI = 1

class SPIKEi2c():

    int_clk = -1

    def tick(self,anz):
        utime.sleep(anz*self.int_clk)

    def GPIO_setup(self,line,state):
        line.direction(state)

    def GPIO_output(self,line,value):
        line.value(value)

    def GPIO_input(self,line):
        return line.value()

    def __init__(self,port, i2c_address,bitrate = 100):
        port.mode(hub.port.MODE_GPIO)
        utime.sleep(0.1)
        self.SCL = port.p5# pin 5
        self.SDA = port.p6# pin 6
        self.SCL.direction(OUT)
        self.SDA.direction(OUT)
        self.SCL.value(HI)
        self.SDA.value(HI)
        self.address = i2c_address

        if bitrate == 100:
            self.int_clk = 0.0000025
        elif bitrate == 400:
            self.int_clk = 0.000000625
        elif bitrate == 1000:
            self.int_clk = 1
        elif bitrate == 3200:
            self.int_clk = 1

    def Start(self):
        #SCL
        #______
        #|    |______
        #SDA
        #___
        #||_________

        self.GPIO_setup(self.SDA, OUT) #configure SDA as output
        self.GPIO_output(self.SDA, HI)
        self.GPIO_output(self.SCL, HI)
        #self.tick(1)
        self.GPIO_output(self.SDA, LOW)
        #self.tick(1)
        self.GPIO_output(self.SCL, LOW)
        #self.tick(2)


    def ReadAck(self):
        self.GPIO_setup(self.SDA, IN)
        readbuffer =0
        for i in range(8):
            self.GPIO_output(self.SCL, HI)
            #self.tick(2)
            readbuffer |= (self.GPIO_input(self.SDA)<< 7) >> i
            self.GPIO_output(self.SCL, LOW)
            #self.tick(2)

        self.GPIO_setup(self.SDA, OUT)
        self.GPIO_output(self.SDA, LOW)
        self.GPIO_output(self.SCL, HI)
        #self.tick(2)
        self.GPIO_output(self.SCL, LOW)
        self.GPIO_output(self.SDA, LOW)
        #self.tick(2)
        return readbuffer

    def ReadNack(self):
        self.GPIO_setup(self.SDA, IN)
        readbuffer =0
        for i in range(8):
            self.GPIO_output(self.SCL, HI)
            #self.tick(2)
            readbuffer |= (self.GPIO_input(self.SDA)<< 7) >> i
            self.GPIO_output(self.SCL, LOW)
            #self.tick(2)

        self.GPIO_setup(self.SDA, OUT)
        self.GPIO_output(self.SDA, HI)
        self.GPIO_output(self.SCL, HI)
        #self.tick(2)
        self.GPIO_output(self.SCL, LOW)
        self.GPIO_output(self.SDA, LOW)
        #self.tick(2)
        return readbuffer

    def WriteByte(self,byte):
        if byte > 0xff:
            return -1
        #print byte
        self.GPIO_setup(self.SDA, OUT)
        for i in range(8):
            #MSB First
            if (byte << i) & 0x80 == 0x80:
                self.GPIO_output(self.SDA, HI)
                self.GPIO_output(self.SCL, HI)
                #self.tick(2)
                self.GPIO_output(self.SCL, LOW)
                self.GPIO_output(self.SDA, LOW)
                #self.tick(2)
            else:
                self.GPIO_output(self.SDA, LOW)
                self.GPIO_output(self.SCL, HI)
                #self.tick(2)
                self.GPIO_output(self.SCL, LOW)
                #self.tick(2)

        self.GPIO_setup(self.SDA, IN)
        self.GPIO_output(self.SCL, HI)
        #self.tick(1)
        #Get The ACK
        #if GPIO.input(self.SDA):
        #    print "ACK"
        #else:
        #    print "NACK"
        #self.tick(2)
        self.GPIO_output(self.SCL, LOW)
        #self.tick(2)

    def Stop(self):
        #SCL
        #_____________
        #|
        #SDA
        #    __________
        #__|
        self.GPIO_setup(self.SDA, OUT) #cnfigure SDA as output

        self.GPIO_output(self.SDA, LOW)
        self.GPIO_output(self.SCL, HI)
        #self.tick(1)
        self.GPIO_output(self.SDA, HI)
        #self.tick(3)

    def readByte(self, reg) :
        self.Start()
        self.WriteByte( self.address)
        self.WriteByte(reg)
        self.Start()
        self.WriteByte( self.address|1)
        result = self.ReadNack()
        self.Stop()
        return (result)

    def readArray(self, reg,len) :
        result =[]
        self.Start()
        self.WriteByte( self.address)
        self.WriteByte(reg)
        self.Start()
        self.WriteByte( self.address|1)
        for i in range(len-1): result.append(self.ReadAck())
        result.append(self.ReadNack())
        self.Stop()
        # print((result), type((result)))
        return bytes(result)


    def writeByte(self,reg,value) :
        self.Start()
        self.WriteByte( self.address)
        self.WriteByte(reg)
        self.WriteByte(value)
        self.Stop()

    def writeArray(self, reg, arr):
        self.Start()
        self.WriteByte( self.address)
        self.WriteByte(reg)
        # print(arr[0], len(arr))
        for i in range(len(arr)): self.WriteByte(arr[i])
        self.Stop()

    def readString(self,reg, length):
        ss = ''
        for x in range(0, length):
            ss = ''.join([ss, chr(self.readByte(reg+x))])
        return ss

    def readInteger(self, reg):
        b0 = self.readByte( reg)
        b1 = self.readByte( reg+1)
        r = b0 + (b1<<8)
        return r

    def readIntegerSigned(self, reg):
        a = self.readInteger(reg)
        #signed_a = ustruct.unpack("<h", a)[0]
        return a

    def readLong(self, reg):
        b0 = self.readByte(reg)
        b1 = self.readByte(reg+1)
        b2 = self.readByte(reg+2)
        b3 = self.readByte(reg+3)
        r = b0 + (b1<<8) + (b2<<16) + (b3<<24)
        return r

    ##Read the firmware version of the i2c device
    def GetFirmwareVersion(self,):
        ver = self.readString(0x00, 8)
        return ver

    ##Read the vendor name of the i2c device
    def GetVendorName(self):
        vendor = self.readString(0x08, 8)
        return vendor

    ##Read the i2c device id
    def GetDeviceId(self):
        device = self.readString(0x10, 8)
        return device





_IO_TIMEOUT = 1000
_SYSRANGE_START = const(0x00)
_EXTSUP_HV = const(0x89)
_MSRC_CONFIG = const(0x60)
_FINAL_RATE_RTN_LIMIT = const(0x44)
_SYSTEM_SEQUENCE = const(0x01)
_SPAD_REF_START = const(0x4f)
_SPAD_ENABLES = const(0xb0)
_REF_EN_START_SELECT = const(0xb6)
_SPAD_NUM_REQUESTED = const(0x4e)
_INTERRUPT_GPIO = const(0x0a)
_INTERRUPT_CLEAR = const(0x0b)
_GPIO_MUX_ACTIVE_HIGH = const(0x84)
_RESULT_INTERRUPT_STATUS = const(0x13)
_RESULT_RANGE_STATUS = const(0x14)
_OSC_CALIBRATE = const(0xf8)
_MEASURE_PERIOD = const(0x04)

SYSRANGE_START = 0x00

SYSTEM_THRESH_HIGH = 0x0C
SYSTEM_THRESH_LOW = 0x0E

SYSTEM_SEQUENCE_CONFIG = 0x01
SYSTEM_RANGE_CONFIG = 0x09
SYSTEM_INTERMEASUREMENT_PERIOD = 0x04

SYSTEM_INTERRUPT_CONFIG_GPIO = 0x0A

GPIO_HV_MUX_ACTIVE_HIGH = 0x84

SYSTEM_INTERRUPT_CLEAR = 0x0B

RESULT_INTERRUPT_STATUS = 0x13
RESULT_RANGE_STATUS = 0x14

RESULT_CORE_AMBIENT_WINDOW_EVENTS_RTN = 0xBC
RESULT_CORE_RANGING_TOTAL_EVENTS_RTN = 0xC0
RESULT_CORE_AMBIENT_WINDOW_EVENTS_REF = 0xD0
RESULT_CORE_RANGING_TOTAL_EVENTS_REF = 0xD4
RESULT_PEAK_SIGNAL_RATE_REF = 0xB6

ALGO_PART_TO_PART_RANGE_OFFSET_MM = 0x28

I2C_SLAVE_DEVICE_ADDRESS = 0x8A

MSRC_CONFIG_CONTROL = 0x60

PRE_RANGE_CONFIG_MIN_SNR = 0x27
PRE_RANGE_CONFIG_VALID_PHASE_LOW = 0x56
PRE_RANGE_CONFIG_VALID_PHASE_HIGH = 0x57
PRE_RANGE_MIN_COUNT_RATE_RTN_LIMIT = 0x64

FINAL_RANGE_CONFIG_MIN_SNR = 0x67
FINAL_RANGE_CONFIG_VALID_PHASE_LOW = 0x47
FINAL_RANGE_CONFIG_VALID_PHASE_HIGH = 0x48
FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = 0x44

PRE_RANGE_CONFIG_SIGMA_THRESH_HI = 0x61
PRE_RANGE_CONFIG_SIGMA_THRESH_LO = 0x62

PRE_RANGE_CONFIG_VCSEL_PERIOD = 0x50
PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x51
PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO = 0x52

SYSTEM_HISTOGRAM_BIN = 0x81
HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT = 0x33
HISTOGRAM_CONFIG_READOUT_CTRL = 0x55

FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x70
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x71
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO = 0x72
CROSSTALK_COMPENSATION_PEAK_RATE_MCPS = 0x20

MSRC_CONFIG_TIMEOUT_MACROP = 0x46

SOFT_RESET_GO2_SOFT_RESET_N = 0xBF
IDENTIFICATION_MODEL_ID = 0xC0
IDENTIFICATION_REVISION_ID = 0xC2

OSC_CALIBRATE_VAL = 0xF8

GLOBAL_CONFIG_VCSEL_WIDTH = 0x32
GLOBAL_CONFIG_SPAD_ENABLES_REF_0 = 0xB0
GLOBAL_CONFIG_SPAD_ENABLES_REF_1 = 0xB1
GLOBAL_CONFIG_SPAD_ENABLES_REF_2 = 0xB2
GLOBAL_CONFIG_SPAD_ENABLES_REF_3 = 0xB3
GLOBAL_CONFIG_SPAD_ENABLES_REF_4 = 0xB4
GLOBAL_CONFIG_SPAD_ENABLES_REF_5 = 0xB5

GLOBAL_CONFIG_REF_EN_START_SELECT = 0xB6
DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD = 0x4E
DYNAMIC_SPAD_REF_EN_START_OFFSET = 0x4F
POWER_MANAGEMENT_GO1_POWER_FORCE = 0x80

VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV = 0x89

ALGO_PHASECAL_LIM = 0x30
ALGO_PHASECAL_CONFIG_TIMEOUT = 0x30


class TimeoutError(RuntimeError):
    pass

class AMHTimer():
    """
    Configurable timer that you can start, reverse, stop and pause.
    By default it counts miliseconds, but you can speed it up,
    Slow it down or accelerate it!
    You can also set the time and reset it.
    You can even run it in reverse, so you can count down until 0.
    It always returns integers, even when you slow it way down.

    Author: Antons Mindstorms Hacks

    Usage
    my_timer = AMHTimer():
    my_timer.rate = 500 # set the rate to 500 ticks/s. That is half the normal rate
    my_timer.acceleration = 100 # Increase the rate by 100 ticks / second squared
    my_timer.reset()
    now = mytimer.time
    """
    def __init__(self, rate=1000, acceleration=0):
        self.running = True
        self.pause_time = 0
        self.reset_at_next_start = False
        self.__speed_factor = rate/1000
        self.__accel_factor = acceleration/1000000
        self.start_time = utime.ticks_ms()

    @property
    def time(self):
        if self.running:
            elapsed = utime.ticks_diff( utime.ticks_ms(), self.start_time )
            return int(
                self.__accel_factor * elapsed**2 +
                self.__speed_factor * elapsed +
                self.pause_time
                )
        else:
            return self.pause_time

    @time.setter
    def time(self, setting):
        self.pause_time = setting
        self.start_time = utime.ticks_ms()

    def pause(self):
        if self.running:
            self.pause_time = self.time
            self.running = False

    def stop(self):
        self.pause()

    def start(self):
        if not self.running:
            self.start_time = utime.ticks_ms()
            self.running = True

    def resume(self):
        self.start()

    def reset(self):
        self.time = 0

    def reverse(self):
        self.rate *= -1

    @property
    def rate(self):
        elapsed = utime.ticks_diff( utime.ticks_ms(), self.start_time )
        return (self.__accel_factor*elapsed + self.__speed_factor) * 1000

    @rate.setter
    def rate(self, setting):
        if self.__speed_factor != setting / 1000:
            if self.running:
                self.pause()
            self.__speed_factor = setting / 1000
            self.start()

    @property
    def acceleration(self, setting):
        return self.__accel_factor * 1000000

    @acceleration.setter
    def acceleration(self, setting):
        if self.__accel_factor != setting / 1000000:
            if self.running:
                self.pause()
            self.__speed_factor = self.rate / 1000
            self.__accel_factor = setting / 1000000
            self.start()


class VL53L0X:
    def __init__(self, port_str, address=0x29):
        port = eval("hub.port." + port_str)
        self.i2c = SPIKEi2c(port, address)
        self.address = address
        self.init()
        self._started = False
        self.measurement_timing_budget_us = 0
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)
        self.enables = {"tcc": 0,
                        "dss": 0,
                        "msrc": 0,
                        "pre_range": 0,
                        "final_range": 0}
        self.timeouts = {"pre_range_vcsel_period_pclks": 0,
                        "msrc_dss_tcc_mclks": 0,
                        "msrc_dss_tcc_us": 0,
                        "pre_range_mclks": 0,
                        "pre_range_us": 0,
                        "final_range_vcsel_period_pclks": 0,
                        "final_range_mclks": 0,
                        "final_range_us": 0
                        }
        self.vcsel_period_type = ["VcselPeriodPreRange", "VcselPeriodFinalRange"]

    def _registers(self, register, values=None, struct='B'):
        if values is None:
            size = ustruct.calcsize(struct)
            data = self.i2c.readArray(register, size)
            # data = self.i2c.readfrom_mem(self.address, register, size)
            values = ustruct.unpack(struct, data)
            return values
        data = ustruct.pack(struct, *values)
        self.i2c.writeArray(register, data)
        # self.i2c.writeto_mem(self.address, register, data)

    def _register(self, register, value=None, struct='B'):
        if value is None:
            return self._registers(register, struct=struct)[0]
        self._registers(register, (value,), struct=struct)

    def _flag(self, register=0x00, bit=0, value=None):
        data = self._register(register)
        mask = 1 << bit
        if value is None:
            return bool(data & mask)
        elif value:
            data |= mask
        else:
            data &= ~mask
        self._register(register, data)

    def _config(self, *config):
        for register, value in config:
            self._register(register, value)

    def init(self, power2v8=True):
        self._flag(_EXTSUP_HV, 0, power2v8)

        # I2C standard mode
        self._config(
            (0x88, 0x00),

            (0x80, 0x01),
            (0xff, 0x01),
            (0x00, 0x00),
        )
        self._stop_variable = self._register(0x91)
        self._config(
            (0x00, 0x01),
            (0xff, 0x00),
            (0x80, 0x00),
        )

        # disable signal_rate_msrc and signal_rate_pre_range limit checks
        self._flag(_MSRC_CONFIG, 1, True)
        self._flag(_MSRC_CONFIG, 4, True)

        # rate_limit = 0.25
        self._register(_FINAL_RATE_RTN_LIMIT, int(0.1 * (1 << 7)),
                    struct='>H')

        self._register(_SYSTEM_SEQUENCE, 0xff)

        spad_count, is_aperture = self._spad_info()
        spad_map = bytearray(self._registers(_SPAD_ENABLES, struct='6B'))

        # set reference spads
        self._config(
            (0xff, 0x01),
            (_SPAD_REF_START, 0x00),
            (_SPAD_NUM_REQUESTED, 0x2c),
            (0xff, 0x00),
            (_REF_EN_START_SELECT, 0xb4),
        )

        spads_enabled = 0
        for i in range(48):
            if i < 12 and is_aperture or spads_enabled >= spad_count:
                spad_map[i // 8] &= ~(1 << (i >> 2))
            elif spad_map[i // 8] & (1 << (i >> 2)):
                spads_enabled += 1

        self._registers(_SPAD_ENABLES, spad_map, struct='6B')

        self._config(
            (0xff, 0x01),
            (0x00, 0x00),

            (0xff, 0x00),
            (0x09, 0x00),
            (0x10, 0x00),
            (0x11, 0x00),

            (0x24, 0x01),
            (0x25, 0xFF),
            (0x75, 0x00),

            (0xFF, 0x01),
            (0x4E, 0x2C),
            (0x48, 0x00),
            (0x30, 0x20),

            (0xFF, 0x00),
            (0x30, 0x09),
            (0x54, 0x00),
            (0x31, 0x04),
            (0x32, 0x03),
            (0x40, 0x83),
            (0x46, 0x25),
            (0x60, 0x00),
            (0x27, 0x00),
            (0x50, 0x06),
            (0x51, 0x00),
            (0x52, 0x96),
            (0x56, 0x08),
            (0x57, 0x30),
            (0x61, 0x00),
            (0x62, 0x00),
            (0x64, 0x00),
            (0x65, 0x00),
            (0x66, 0xA0),

            (0xFF, 0x01),
            (0x22, 0x32),
            (0x47, 0x14),
            (0x49, 0xFF),
            (0x4A, 0x00),

            (0xFF, 0x00),
            (0x7A, 0x0A),
            (0x7B, 0x00),
            (0x78, 0x21),

            (0xFF, 0x01),
            (0x23, 0x34),
            (0x42, 0x00),
            (0x44, 0xFF),
            (0x45, 0x26),
            (0x46, 0x05),
            (0x40, 0x40),
            (0x0E, 0x06),
            (0x20, 0x1A),
            (0x43, 0x40),

            (0xFF, 0x00),
            (0x34, 0x03),
            (0x35, 0x44),

            (0xFF, 0x01),
            (0x31, 0x04),
            (0x4B, 0x09),
            (0x4C, 0x05),
            (0x4D, 0x04),

            (0xFF, 0x00),
            (0x44, 0x00),
            (0x45, 0x20),
            (0x47, 0x08),
            (0x48, 0x28),
            (0x67, 0x00),
            (0x70, 0x04),
            (0x71, 0x01),
            (0x72, 0xFE),
            (0x76, 0x00),
            (0x77, 0x00),

            (0xFF, 0x01),
            (0x0D, 0x01),

            (0xFF, 0x00),
            (0x80, 0x01),
            (0x01, 0xF8),

            (0xFF, 0x01),
            (0x8E, 0x01),
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )

        self._register(_INTERRUPT_GPIO, 0x04)
        self._flag(_GPIO_MUX_ACTIVE_HIGH, 4, False)
        self._register(_INTERRUPT_CLEAR, 0x01)

        # XXX Need to implement this.
        # budget = self._timing_budget()
        # self._register(_SYSTEM_SEQUENCE, 0xe8)
        # self._timing_budget(budget)

        self._register(_SYSTEM_SEQUENCE, 0x01)
        self._calibrate(0x40)
        self._register(_SYSTEM_SEQUENCE, 0x02)
        self._calibrate(0x00)

        self._register(_SYSTEM_SEQUENCE, 0xe8)

    def _spad_info(self):
        self._config(
            (0x80, 0x01),
            (0xff, 0x01),
            (0x00, 0x00),

            (0xff, 0x06),
        )
        self._flag(0x83, 3, True)
        self._config(
            (0xff, 0x07),
            (0x81, 0x01),

            (0x80, 0x01),

            (0x94, 0x6b),
            (0x83, 0x00),
        )
        for timeout in range(_IO_TIMEOUT):
            if self._register(0x83):
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        self._config(
            (0x83, 0x01),
        )
        value = self._register(0x92)
        self._config(
            (0x81, 0x00),
            (0xff, 0x06),
        )
        self._flag(0x83, 3, False)
        self._config(
            (0xff, 0x01),
            (0x00, 0x01),

            (0xff, 0x00),
            (0x80, 0x00),
        )
        count = value & 0x7f
        is_aperture = bool(value & 0b10000000)
        return count, is_aperture

    def _calibrate(self, vhv_init_byte):
        self._register(_SYSRANGE_START, 0x01 | vhv_init_byte)
        for timeout in range(_IO_TIMEOUT):
            if self._register(_RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        self._register(_INTERRUPT_CLEAR, 0x01)
        self._register(_SYSRANGE_START, 0x00)

    def start(self, period=0):
        self._config(
            (0x80, 0x01),
            (0xFF, 0x01),
            (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )
        if period:
            oscilator = self._register(_OSC_CALIBRATE, struct='>H')
            if oscilator:
                period *= oscilator
            self._register(_MEASURE_PERIOD, period, struct='>H')
            self._register(_SYSRANGE_START, 0x04)
        else:
            self._register(_SYSRANGE_START, 0x02)
        self._started = True

    def stop(self):
        self._register(_SYSRANGE_START, 0x01)
        self._config(
            (0xFF, 0x01),
            (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01),
            (0xFF, 0x00),
        )
        self._started = False

    def read(self):
        if not self._started:
            self._config(
                (0x80, 0x01),
                (0xFF, 0x01),
                (0x00, 0x00),
                (0x91, self._stop_variable),
                (0x00, 0x01),
                (0xFF, 0x00),
                (0x80, 0x00),
                (_SYSRANGE_START, 0x01),
            )
            for timeout in range(_IO_TIMEOUT):
                if not self._register(_SYSRANGE_START) & 0x01:
                    break
                utime.sleep_ms(1)
            else:
                raise TimeoutError()
        for timeout in range(_IO_TIMEOUT):
            if self._register(_RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        value = self._register(_RESULT_RANGE_STATUS + 10, struct='>H')
        self._register(_INTERRUPT_CLEAR, 0x01)
        return value

    def set_signal_rate_limit(self, limit_Mcps):
        if limit_Mcps < 0 or limit_Mcps > 511.99:
            return False
        self._register(0x44, limit_Mcps * (1 << 7))
        return True

    def decode_Vcsel_period(self, reg_val):
        return (((reg_val) + 1) << 1)

    def encode_Vcsel_period(self, period_pclks):
        return (((period_pclks) >> 1) - 1)

    def set_Vcsel_pulse_period(self, type, period_pclks):
        vcsel_period_reg = self.encode_Vcsel_period(period_pclks)

        self.get_sequence_step_enables()
        self.get_sequence_step_timeouts()

        if type == self.vcsel_period_type[0]:
            if period_pclks == 12:
                self._register(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x18)
            elif period_pclks == 14:
                self._register(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x30)
            elif period_pclks == 16:
                self._register(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x40)
            elif period_pclks == 18:
                self._register(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x50)
            else:
                return False

            self._register(PRE_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)
            self._register(PRE_RANGE_CONFIG_VCSEL_PERIOD, vcsel_period_reg)

            new_pre_range_timeout_mclks = self.timeout_microseconds_to_Mclks(self.timeouts["pre_range_us"],
                                                                            period_pclks)
            self._register(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI, self.encode_timeout(new_pre_range_timeout_mclks))

            new_msrc_timeout_mclks = self.timeout_microseconds_to_Mclks(self.timeouts["msrc_dss_tcc_us"],
                                                                        period_pclks)
            self._register(MSRC_CONFIG_TIMEOUT_MACROP, 255 if new_msrc_timeout_mclks > 256 else (new_msrc_timeout_mclks - 1))
        elif type == self.vcsel_period_type[1]:
            if period_pclks == 8:
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x10)
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)
                self._register(GLOBAL_CONFIG_VCSEL_WIDTH, 0x02)
                self._(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x0C)
                self._register(0xFF, 0x01)
                self._register(ALGO_PHASECAL_LIM, 0x30)
                self._register(0xFF, 0x00)
            elif period_pclks == 10:
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x28)
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)
                self._register(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                self._register(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x09)
                self._register(0xFF, 0x01)
                self._register(ALGO_PHASECAL_LIM, 0x20)
                self._register(0xFF, 0x00)
            elif period_pclks == 12:
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x38)
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)
                self._register(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                self._register(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x08)
                self._register(0xFF, 0x01)
                self._register(ALGO_PHASECAL_LIM, 0x20)
                self._register(0xFF, 0x00)
            elif period_pclks == 14:
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x48)
                self._register(FINAL_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)
                self._register(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                self._register(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x07)
                self._register(0xFF, 0x01)
                self._register(ALGO_PHASECAL_LIM, 0x20)
                self._register(0xFF, 0x00)
            else:
                return False

            self._register(FINAL_RANGE_CONFIG_VCSEL_PERIOD, vcsel_period_reg)

            new_final_range_timeout_mclks = self.timeout_microseconds_to_Mclks(self.timeouts["final_range_us"], period_pclks)

            if self.enables["pre_range"]:
                new_final_range_timeout_mclks += 1
            self._register(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI, self.encode_timeout(new_final_range_timeout_mclks))
        else:
            return False
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)
        sequence_config = self._register(SYSTEM_SEQUENCE_CONFIG)
        self._register(SYSTEM_SEQUENCE_CONFIG, 0x02)
        self.perform_single_ref_calibration(0x0)
        self._register(SYSTEM_SEQUENCE_CONFIG, sequence_config)

        return True

    def get_sequence_step_enables(self):
        sequence_config = self._register(0x01)

        self.enables["tcc"] = (sequence_config >> 4) & 0x1
        self.enables["dss"] = (sequence_config >> 3) & 0x1
        self.enables["msrc"] = (sequence_config >> 2) & 0x1
        self.enables["pre_range"] = (sequence_config >> 6) & 0x1
        self.enables["final_range"] = (sequence_config >> 7) & 0x1

    def get_vcsel_pulse_period(self, type):
        if type == self.vcsel_period_type[0]:
            return self.decode_Vcsel_period(0x50)
        elif type == self.vcsel_period_type[1]:
            return self.decode_Vcsel_period(0x70)
        else:
            return 255

    def get_sequence_step_timeouts(self):
        self.timeouts["pre_range_vcsel_period_pclks"] = self.get_vcsel_pulse_period(self.vcsel_period_type[0])
        self.timeouts["msrc_dss_tcc_mclks"] = int(self._register(MSRC_CONFIG_TIMEOUT_MACROP)) + 1
        self.timeouts["msrc_dss_tcc_us"] = self.timeout_Mclks_to_microseconds(self.timeouts["msrc_dss_tcc_mclks"],
                                                                            self.timeouts[
                                                                                "pre_range_vcsel_period_pclks"])
        self.timeouts["pre_range_mclks"] = self.decode_timeout(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI)
        self.timeouts["pre_range_us"] = self.timeout_Mclks_to_microseconds(self.timeouts["pre_range_mclks"],
                                                                        self.timeouts[
                                                                            "pre_range_vcsel_period_pclks"])
        self.timeouts["final_range_vcsel_period_pclks"] = self.get_vcsel_pulse_period(self.vcsel_period_type[1])
        self.timeouts["final_range_mclks"] = self.decode_timeout(self._register(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI))

        if self.enables["pre_range"]:
            self.timeouts["final_range_mclks"] -= self.timeouts["pre_range_mclks"]
        self.timeouts["final_range_us"] = self.timeout_Mclks_to_microseconds(self.timeouts["final_range_mclks"],
                                                                            self.timeouts[
                                                                                "final_range_vcsel_period_pclks"])

    def timeout_Mclks_to_microseconds(self, timeout_period_mclks, vcsel_period_pclks):
        macro_period_ns = self.calc_macro_period(vcsel_period_pclks)
        return ((timeout_period_mclks * macro_period_ns) + (macro_period_ns / 2)) / 1000

    def timeout_microseconds_to_Mclks(self, timeout_period_us, vcsel_period_pclks):
        macro_period_ns = self.calc_macro_period(vcsel_period_pclks)
        return (((timeout_period_us * 1000) + (macro_period_ns / 2)) / macro_period_ns)

    def calc_macro_period(self, vcsel_period_pclks):
        return (((2304 * (vcsel_period_pclks) * 1655) + 500) / 1000)

    def decode_timeout(self, reg_val):
        return ((reg_val & 0x00FF) << ((reg_val & 0xFF00) >> 8)) + 1

    def encode_timeout(self, timeout_mclks):
        timeout_mclks = int(timeout_mclks)
        ls_byte = 0
        ms_byte = 0

        if timeout_mclks > 0:
            ls_byte = timeout_mclks - 1

            while (ls_byte & 0xFFFFFF00) > 0:
                ls_byte >>= 1
                ms_byte += 1
            return (ms_byte << 8) or (ls_byte & 0xFF)
        else:
            return 0

    def set_measurement_timing_budget(self, budget_us):
        start_overhead = 1320
        end_overhead = 960
        msrc_overhead = 660
        tcc_overhead = 590
        dss_overhead = 690
        pre_range_overhead = 660
        final_range_overhead = 550

        min_timing_budget = 20000

        if budget_us < min_timing_budget:
            return False
        used_budget_us = start_overhead + end_overhead

        self.get_sequence_step_enables()
        self.get_sequence_step_timeouts()

        if self.enables["tcc"]:
            used_budget_us += self.timeouts["msrc_dss_tcc_us"] + tcc_overhead
        if self.enables["dss"]:
            used_budget_us += 2* self.timeouts["msrc_dss_tcc_us"] + dss_overhead
        if self.enables["msrc"]:
            used_budget_us += self.timeouts["msrc_dss_tcc_us"] + msrc_overhead
        if self.enables["pre_range"]:
            used_budget_us += self.timeouts["pre_range_us"] + pre_range_overhead
        if self.enables["final_range"]:
            used_budget_us += final_range_overhead

            if used_budget_us > budget_us:
                return False
            final_range_timeout_us = budget_us - used_budget_us
            final_range_timeout_mclks = self.timeout_microseconds_to_Mclks(final_range_timeout_us, self.timeouts["final_range_vcsel_period_pclks"])

            if self.enables["pre_range"]:
                final_range_timeout_mclks += self.timeouts["pre_range_mclks"]
            self._register(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI, self.encode_timeout(final_range_timeout_mclks))
            self.measurement_timing_budget_us = budget_us
        return True

    def perform_single_ref_calibration(self, vhv_init_byte):
        chrono = AMHTimer()
        self._register(SYSRANGE_START, 0x01|vhv_init_byte)
        chrono.start()
        while self._register((RESULT_INTERRUPT_STATUS & 0x07) == 0):
            time_elapsed = chrono.time
            if time_elapsed > _IO_TIMEOUT:
                return False
        self._register(SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._register(SYSRANGE_START, 0x00)
        return True


tof = VL53L0X('E')

tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)

tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

while True:
# Start ranging
    tof.start()
    print(tof.read())
    tof.stop()
from micropython import const
import ustruct
import utime
from machine import I2C

IO_TIMEOUT = 1000
SYSRANGE_START = const(0x00)
EXTSUP_HV = const(0x89)
MSRCconfig = const(0x60)
FINAL_RATE_RTN_LIMIT = const(0x44)
SYSTEM_SEQUENCE = const(0x01)
SPAD_REF_START = const(0x4f)
SPAD_ENABLES = const(0xb0)
REF_EN_START_SELECT = const(0xb6)
SPAD_NUM_REQUESTED = const(0x4e)
INTERRUPT_GPIO = const(0x0a)
INTERRUPT_CLEAR = const(0x0b)
GPIO_MUX_ACTIVE_HIGH = const(0x84)
RESULT_INTERRUPT_STATUS = const(0x13)
RESULT_RANGE_STATUS = const(0x14)
OSCcalibrate = const(0xf8)
MEASURE_PERIOD = const(0x04)

class TimeoutError(RuntimeError):
    pass

class VL53L0X:
    def __init__(self, address, _scl, _sda):
        self.bus = I2C(0, scl=_scl, sda=_sda)
        self.address = address
        self.init()
        self.started = False

    def registers(self, register, values=None, struct='B'):
        if values is None:
            size = ustruct.calcsize(struct)
            data = self.bus.readfrom_mem(self.address, register, size)
            values = ustruct.unpack(struct, data)
            return values
        data = ustruct.pack(struct, *values)
        self.bus.writeto_mem(self.address, register, data)

    def register(self, register, value=None, struct='B'):
        if value is None:
            return self.registers(register, struct=struct)[0]
        self.registers(register, (value,), struct=struct)

    def flag(self, register=0x00, bit=0, value=None):
        data = self.register(register)
        mask = 1 << bit
        if value is None:
            return bool(data & mask)
        elif value:
            data |= mask
        else:
            data &= ~mask
        self.register(register, data)

    def config(self, *config):
        for register, value in config:
            self.register(register, value)

    def calibrate(self, vhv_init_byte):
        self.register(SYSRANGE_START, 0x01 | vhv_init_byte)
        for timeout in range(IO_TIMEOUT):
            if self.register(RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        self.register(INTERRUPT_CLEAR, 0x01)
        self.register(SYSRANGE_START, 0x00)

    def _spad_info(self):
        self.config(
            (0x80, 0x01), (0xff, 0x01),
            (0x00, 0x00),

            (0xff, 0x06),
        )
        self.flag(0x83, 3, True)
        self.config(
            (0xff, 0x07), (0x81, 0x01),

            (0x80, 0x01),

            (0x94, 0x6b), (0x83, 0x00),
        )
        for timeout in range(IO_TIMEOUT):
            if self.register(0x83):
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        self.config(
            (0x83, 0x01),
        )
        value = self.register(0x92)
        self.config(
            (0x81, 0x00), (0xff, 0x06),
        )
        self.flag(0x83, 3, False)
        self.config(
            (0xff, 0x01), (0x00, 0x01),

            (0xff, 0x00), (0x80, 0x00),
        )
        count = value & 0x7f
        is_aperture = bool(value & 0b10000000)
        return count, is_aperture

    def init(self, power2v8=True):
        self.flag(EXTSUP_HV, 0, power2v8)

        # I2C standard mode
        self.config(
            (0x88, 0x00),

            (0x80, 0x01), (0xff, 0x01),
            (0x00, 0x00),
        )
        self.stop_variable = self.register(0x91)
        self.config(
            (0x00, 0x01), (0xff, 0x00),
            (0x80, 0x00),
        )

        # disable signal_rate_msrc and signal_rate_pre_range limit checks
        self.flag(MSRCconfig, 1, True)
        self.flag(MSRCconfig, 4, True)

        # rate_limit = 0.25
        self.register(FINAL_RATE_RTN_LIMIT, int(0.25 * (1 << 7)),
                       struct='>H')

        self.register(SYSTEM_SEQUENCE, 0xff)

        spad_count, is_aperture = self._spad_info()
        spad_map = bytearray(self.registers(SPAD_ENABLES, struct='6B'))

        # set reference spads
        self.config(
            (0xff, 0x01),
            (SPAD_REF_START, 0x00),
            (SPAD_NUM_REQUESTED, 0x2c),
            (0xff, 0x00),
            (REF_EN_START_SELECT, 0xb4),
        )

        spads_enabled = 0
        for i in range(48):
            if i < 12 and is_aperture or spads_enabled >= spad_count:
                spad_map[i // 8] &= ~(1 << (i >> 2))
            elif spad_map[i // 8] & (1 << (i >> 2)):
                spads_enabled += 1

        self.registers(SPAD_ENABLES, spad_map, struct='6B')

        self.config(
            (0xff, 0x01), (0x00, 0x00),

            (0xff, 0x00), (0x09, 0x00),
            (0x10, 0x00), (0x11, 0x00),

            (0x24, 0x01), (0x25, 0xFF),
            (0x75, 0x00),

            (0xFF, 0x01), (0x4E, 0x2C),
            (0x48, 0x00), (0x30, 0x20),

            (0xFF, 0x00), (0x30, 0x09),
            (0x54, 0x00), (0x31, 0x04),
            (0x32, 0x03), (0x40, 0x83),
            (0x46, 0x25), (0x60, 0x00),
            (0x27, 0x00), (0x50, 0x06),
            (0x51, 0x00), (0x52, 0x96),
            (0x56, 0x08), (0x57, 0x30),
            (0x61, 0x00), (0x62, 0x00),
            (0x64, 0x00), (0x65, 0x00),
            (0x66, 0xA0),

            (0xFF, 0x01), (0x22, 0x32),
            (0x47, 0x14), (0x49, 0xFF),
            (0x4A, 0x00),

            (0xFF, 0x00), (0x7A, 0x0A),
            (0x7B, 0x00), (0x78, 0x21),

            (0xFF, 0x01), (0x23, 0x34),
            (0x42, 0x00), (0x44, 0xFF),
            (0x45, 0x26), (0x46, 0x05),
            (0x40, 0x40), (0x0E, 0x06),
            (0x20, 0x1A), (0x43, 0x40),

            (0xFF, 0x00), (0x34, 0x03),
            (0x35, 0x44),

            (0xFF, 0x01), (0x31, 0x04),
            (0x4B, 0x09), (0x4C, 0x05),
            (0x4D, 0x04),

            (0xFF, 0x00), (0x44, 0x00),
            (0x45, 0x20), (0x47, 0x08),
            (0x48, 0x28), (0x67, 0x00),
            (0x70, 0x04), (0x71, 0x01),
            (0x72, 0xFE), (0x76, 0x00),
            (0x77, 0x00),

            (0xFF, 0x01), (0x0D, 0x01),

            (0xFF, 0x00), (0x80, 0x01),
            (0x01, 0xF8),

            (0xFF, 0x01), (0x8E, 0x01),
            (0x00, 0x01), (0xFF, 0x00),
            (0x80, 0x00),
        )

        self.register(INTERRUPT_GPIO, 0x04)
        self.flag(GPIO_MUX_ACTIVE_HIGH, 4, False)
        self.register(INTERRUPT_CLEAR, 0x01)

        self.register(SYSTEM_SEQUENCE, 0x01)
        self.calibrate(0x40)
        self.register(SYSTEM_SEQUENCE, 0x02)
        self.calibrate(0x00)

        self.register(SYSTEM_SEQUENCE, 0xe8)

    def start(self, period=0):
        self.config(
          (0x80, 0x01), (0xFF, 0x01),
          (0x00, 0x00), (0x91, self.stop_variable),
          (0x00, 0x01), (0xFF, 0x00),
          (0x80, 0x00),
        )
        if period:
            oscilator = self.register(OSCcalibrate, struct='>H')
            if oscilator:
                period *= oscilator
            self.register(MEASURE_PERIOD, period, struct='>H')
            self.register(SYSRANGE_START, 0x04)
        else:
            self.register(SYSRANGE_START, 0x02)
        self.started = True

    def stop(self):
        self.register(SYSRANGE_START, 0x01)
        self.config(
          (0xFF, 0x01), (0x00, 0x00),
          (0x91, self.stop_variable), (0x00, 0x01),
          (0xFF, 0x00),
        )
        self.started = False

    def read(self):
        if not self.started:
            self.config(
              (0x80, 0x01), (0xFF, 0x01),
              (0x00, 0x00), (0x91, self.stop_variable),
              (0x00, 0x01), (0xFF, 0x00),
              (0x80, 0x00), (SYSRANGE_START, 0x01),
            )
            for timeout in range(IO_TIMEOUT):
                if not self.register(SYSRANGE_START) & 0x01:
                    break
                utime.sleep_ms(1)
            else:
                raise TimeoutError()
        for timeout in range(IO_TIMEOUT):
            if self.register(RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise TimeoutError()
        value = self.register(RESULT_RANGE_STATUS + 10, struct='>H')
        self.register(INTERRUPT_CLEAR, 0x01)
        return value

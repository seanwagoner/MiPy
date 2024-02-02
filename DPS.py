import machine
from machine import I2C
import utime as time


def getTwosComplement(raw_val, length):
        if raw_val & (1 << (length - 1)):
            raw_val = raw_val - (1 << length)
        return raw_val

class DPS:

    def __init__(self, scl_pin, sda_pin, addr=0x77):
        self.bus = machine.I2C(0, scl='P6_0', sda='P6_1')
        self.addr = addr
        self.__kP = 1040384
        self.__kT = 1040384
        self.__correctTemperature()
        self.__setOversamplingRate()

    def __correctTemperature(self):
        DPS.__bus.write_byte_data(DPS.__addr, 0x0E, 0xA5)
        DPS.__bus.write_byte_data(DPS.__addr, 0x0F, 0x96)
        DPS.__bus.write_byte_data(DPS.__addr, 0x62, 0x02)
        DPS.__bus.write_byte_data(DPS.__addr, 0x0E, 0x00)
        DPS.__bus.write_byte_data(DPS.__addr, 0x0F, 0x00)

    def __setOversamplingRate(self):
        DPS.__bus.write_byte_data(DPS.__addr, 0x06, 0x26)
        DPS.__bus.write_byte_data(DPS.__addr, 0x07, 0xA6)
        DPS.__bus.write_byte_data(DPS.__addr, 0x08, 0x07)
        DPS.__bus.write_byte_data(DPS.__addr, 0x09, 0x0C)

    def __getRawPressure(self):
        p1 = DPS.__bus.read_byte_data(DPS.__addr, 0x00)
        p2 = DPS.__bus.read_byte_data(DPS.__addr, 0x01)
        p3 = DPS.__bus.read_byte_data(DPS.__addr, 0x02)

        p = (p1 << 16) | (p2 << 8) | p3
        p = getTwosComplement(p, 24)

        return p

    def __getRawTemperature(self):
        t1 = DPS.__bus.read_byte_data(DPS.__addr, 0x03)
        t2 = DPS.__bus.read_byte_data(DPS.__addr, 0x04)
        t3 = DPS.__bus.read_byte_data(DPS.__addr, 0x05)

        t = (t1 << 16) | (t2 << 8) | t3
        t = getTwosComplement(t, 24)
        return t

    def __getPressureCalibrationCoefficients(self):
        src13 = DPS.__bus.read_byte_data(DPS.__addr, 0x13)
        src14 = DPS.__bus.read_byte_data(DPS.__addr, 0x14)
        src15 = DPS.__bus.read_byte_data(DPS.__addr, 0x15)
        src16 = DPS.__bus.read_byte_data(DPS.__addr, 0x16)
        src17 = DPS.__bus.read_byte_data(DPS.__addr, 0x17)
        src18 = DPS.__bus.read_byte_data(DPS.__addr, 0x18)
        src19 = DPS.__bus.read_byte_data(DPS.__addr, 0x19)
        src1A = DPS.__bus.read_byte_data(DPS.__addr, 0x1A)
        src1B = DPS.__bus.read_byte_data(DPS.__addr, 0x1B)
        src1C = DPS.__bus.read_byte_data(DPS.__addr, 0x1C)
        src1D = DPS.__bus.read_byte_data(DPS.__addr, 0x1D)
        src1E = DPS.__bus.read_byte_data(DPS.__addr, 0x1E)
        src1F = DPS.__bus.read_byte_data(DPS.__addr, 0x1F)
        src20 = DPS.__bus.read_byte_data(DPS.__addr, 0x20)
        src21 = DPS.__bus.read_byte_data(DPS.__addr, 0x21)

        c00 = (src13 << 12) | (src14 << 4) | (src15 >> 4)
        c00 = getTwosComplement(c00, 20)

        c10 = ((src15 & 0x0F) << 16) | (src16 << 8) | src17
        c10 = getTwosComplement(c10, 20)

        c20 = (src1C << 8) | src1D
        c20 = getTwosComplement(c20, 16)

        c30 = (src20 << 8) | src21
        c30 = getTwosComplement(c30, 16)

        c01 = (src18 << 8) | src19
        c01 = getTwosComplement(c01, 16)

        c11 = (src1A << 8) | src1B
        c11 = getTwosComplement(c11, 16)

        c21 = (src1E << 8) | src1F
        c21 = getTwosComplement(c21, 16)

        return c00, c10, c20, c30, c01, c11, c21


    def __getTemperatureCalibrationCoefficients(self):

        src10 = DPS.__bus.read_byte_data(DPS.__addr, 0x10)
        src11 = DPS.__bus.read_byte_data(DPS.__addr, 0x11)
        src12 = DPS.__bus.read_byte_data(DPS.__addr, 0x12)
        c0 = (src10 << 4) | (src11 >> 4)
        c0 = getTwosComplement(c0, 12)

        c1 = ((src11 & 0x0F) << 8) | src12
        c1 = getTwosComplement(c1, 12)

        return c0, c1


    def calcScaledPressure(self):
        raw_p = self.__getRawPressure()
        scaled_p = raw_p / DPS.__kP
        return scaled_p


    def calcScaledTemperature(self):
        raw_t = self.__getRawTemperature()
        scaled_t = raw_t / DPS.__kT
        return scaled_t

    def calcCompTemperature(self, scaled_t):
        c0, c1 = self.__getTemperatureCalibrationCoefficients()
        comp_t = c0 * 0.5 + scaled_t * c1
        return comp_t


    def calcCompPressure(self, scaled_p, scaled_t):
        c00, c10, c20, c30, c01, c11, c21 = self.__getPressureCalibrationCoefficients(
        comp_p = (c00 + scaled_p * (c10 + scaled_p * (c20 + scaled_p * c30))
                + scaled_t * (c01 + scaled_p * (c11 + scaled_p * c21)))

        return comp_p
    
    def measureTemperatureOnce(self):       
        t= self.calcScaledTemperature()
        temperature=self.calcCompTemperature(t)       
        return temperature
        

    def measurePressureOnce(self):        
        p = self.calcScaledPressure()
        t= self.calcScaledTemperature()
        pressure =self.calcCompPressure(p, t) 
        return pressure
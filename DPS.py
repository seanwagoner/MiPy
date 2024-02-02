import machine
from machine import I2C
import utime as time

def getTwosComplement(raw_val, length):
        if raw_val & (1 << (length - 1)):
            raw_val = raw_val - (1 << length)
        return raw_val

class DPS:

    def __init__(self, scl_pin, sda_pin, addr=0x77):
        self.addr = addr
        self.kP = 1040384
        self.kT = 1040384
        self.bus = machine.I2C(0, scl='P6_0', sda='P6_1')
        self.correctTemperature()
        self.setOversamplingRate()

    def correctTemperature(self):
        self.bus.writeto(self.addr, bytes([0x0E, 0xA5]))
        self.bus.writeto(self.addr, bytes([0x0F, 0x96]))
        self.bus.writeto(self.addr, bytes([0x62, 0x02]))
        self.bus.writeto(self.addr, bytes([0x0E, 0x00]))
        self.bus.writeto(self.addr, bytes([0x0F, 0x00]))
 
    def setOversamplingRate(self):
        self.bus.writeto(self.addr, bytes([0x06, 0x26]))
        self.bus.writeto(self.addr, bytes([0x07, 0xA6]))
        self.bus.writeto(self.addr, bytes([0x08, 0x07]))
        self.bus.writeto(self.addr, bytes([0x09, 0x0C]))

    def getRawPressure(self):
        self.bus.writeto(self.addr, bytes([0x00]))
        p_bytes = self.bus.readfrom(self.addr, 3)
        p = int.from_bytes(p_bytes, 'big') & 0xFFFFFF
        return getTwosComplement(p, 24)

    def getRawTemperature(self):
        self.bus.writeto(self.addr, bytes([0x03]))
        t_bytes = self.bus.readfrom(self.addr, 3)
        t = int.from_bytes(t_bytes, 'big') & 0xFFFFFF
        return getTwosComplement(t, 24)

    def getPressureCalibrationCoefficients(self):
        coefficients = []
        for reg in range(0x13, 0x22):
            self.bus.writeto(self.addr, bytes([reg]))
            coeff_byte = self.bus.readfrom(self.addr, 1)
            coefficients.append(coeff_byte[0])
    
        c00 = self._combineCoefficients(coefficients[0:3], 20)
        c10 = self._combineCoefficients(coefficients[3:6], 20)
        c20 = self._combineCoefficients(coefficients[6:8], 16)
        c30 = self._combineCoefficients(coefficients[14:16], 16)
        c01 = self._combineCoefficients(coefficients[8:10], 16)
        c11 = self._combineCoefficients(coefficients[10:12], 16)
        c21 = self._combineCoefficients(coefficients[12:14], 16)

        return c00, c10, c20, c30, c01, c11, c21

    def _combineCoefficients(self, bytes_list, length):
        combined = 0
        for i, byte in enumerate(bytes_list):
            combined |= byte << (8 * (len(bytes_list) - i - 1))
        return getTwosComplement(combined, length)

    def getTemperatureCalibrationCoefficients(self):
        self.bus.writeto(self.addr, bytes([0x10]))
        src10 = int.from_bytes(self.bus.readfrom(self.addr, 1), 'big')
        self.bus.writeto(self.addr, bytes([0x11]))
        src11 = int.from_bytes(self.bus.readfrom(self.addr, 1), 'big')
        self.bus.writeto(self.addr, bytes([0x12]))
        src12 = int.from_bytes(self.bus.readfrom(self.addr, 1), 'big')

        c0 = (src10 << 4) | (src11 >> 4)
        c0 = getTwosComplement(c0, 12)
        c1 = ((src11 & 0x0F) << 8) | src12
        c1 = getTwosComplement(c1, 12)
        return c0, c1

    def calcScaledPressure(self):
        raw_p = self.getRawPressure()
        scaled_p = raw_p / self.kP
        return scaled_p

    def calcScaledTemperature(self):
        raw_t = self.getRawTemperature()
        scaled_t = raw_t / self.kT
        return scaled_t

    def calcCompTemperature(self, scaled_t):
        c0, c1 = self.getTemperatureCalibrationCoefficients()
        comp_t = c0 * 0.5 + c1 * scaled_t
        return comp_t

    def calcCompPressure(self, scaled_p, scaled_t):
        c00, c10, c20, c30, c01, c11, c21 = self.getPressureCalibrationCoefficients()
        comp_p = (c00 + scaled_p * (c10 + scaled_p * (c20 + scaled_p * c30))
                + scaled_t * (c01 + scaled_p * (c11 + scaled_p * c21)))
        return comp_p

    def measureTemperatureOnce(self):       
        t = self.calcScaledTemperature()
        temperature = self.calcCompTemperature(t)       
        return temperature
        
    def measurePressureOnce(self):        
        p = self.calcScaledPressure()
        t = self.calcScaledTemperature()
        pressure = self.calcCompPressure(p, t) 
        return pressure
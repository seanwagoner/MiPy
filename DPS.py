import machine
from machine import I2C
import utime as time

def getTwosComplement(raw_val, length):
    """Get two's complement of `raw_val`.
        Args:
            raw_val (int): Raw value
            length (int): Max bit length
        Returns:
            int: Two's complement
        """
        if raw_val & (1 << (length - 1)):
            raw_val = raw_val - (1 << length)
        return raw_val

class DPS:

    """Class of DPS, Pressure and Temperature sensor.
    """

    def __init__(self, scl_pin, sda_pin, addr=0x77):

        # Compensation Scale Factors

        # Oversampling Rate          | Scale Factor (kP or kT)

        # ---------------------------|------------------------

        #   1       (single)         |  524288 

        #   2 times (Low Power)      | 1572864

        #   4 times                  | 3670016

        #   8 times                  | 7864320

        #  16 times (Standard)       |  253952

        #  32 times                  |  516096

        #  64 times (High Precision) | 1040384  <- Configured

        # 128 times                  | 2088960

        """Initial setting.
        Execute `self.correctTemperature()` and `self.setOversamplingRate()`.
        """

        self.addr = addr
        self.kP = 1040384
        self.kT = 1040384
        self.bus = machine.I2C(0, scl='P6_0', sda='P6_1')
        self.correctTemperature()
        self.setOversamplingRate()

    def correctTemperature(self):
        """
        Corrects the temperature readings from the DPS sensor.

        Issue: The DPS sensor occasionally reports abnormally high temperature values, 
        significantly above the actual ambient temperature (e.g., showing over 60°C in 
        a 20-30°C environment).

        Purpose: This function addresses this issue by recalibrating or adjusting the 
        sensor's temperature measurement system. It writes specific calibration values 
        to the sensor's registers, ensuring more accurate and reliable temperature readings.

        Usage: Call this method after initializing the DPS sensor to ensure temperature 
        readings are corrected for the sensor's anomaly. It's particularly recommended if 
        you encounter inconsistent or weirdly high temperature readings.

        Note: The specific values written to the sensor's registers (0xA5, 0x96, etc.) 
        have been based on the sensor's datasheet and empirical adjustments to 
        counteract the reported issue.
        """
        self.bus.writeto(self.addr, bytes([0x0E, 0xA5]))
        self.bus.writeto(self.addr, bytes([0x0F, 0x96]))
        self.bus.writeto(self.addr, bytes([0x62, 0x02]))
        self.bus.writeto(self.addr, bytes([0x0E, 0x00]))
        self.bus.writeto(self.addr, bytes([0x0F, 0x00]))
 
    def setOversamplingRate(self):
        """Set oversampling rate.
        Pressure measurement rate    :  4 Hz
        Pressure oversampling rate   : 64 times
        Temperature measurement rate :  4 Hz
        Temperature oversampling rate: 64 times
        """
        self.bus.writeto(self.addr, bytes([0x06, 0x26]))
        self.bus.writeto(self.addr, bytes([0x07, 0xA6]))
        self.bus.writeto(self.addr, bytes([0x08, 0x07]))
        self.bus.writeto(self.addr, bytes([0x09, 0x0C]))

    def getRawPressure(self):
        """Get raw pressure from sensor.
        Returns:
            int: Raw pressure
        """
        self.bus.writeto(self.addr, bytes([0x00]))
        p_bytes = self.bus.readfrom(self.addr, 3)
        p = int.from_bytes(p_bytes, 'big') & 0xFFFFFF
        return getTwosComplement(p, 24)

    def getRawTemperature(self):
        """Get raw temperature from sensor.
        Returns:
            int: Raw temperature
        """
        self.bus.writeto(self.addr, bytes([0x03]))
        t_bytes = self.bus.readfrom(self.addr, 3)
        t = int.from_bytes(t_bytes, 'big') & 0xFFFFFF
        return getTwosComplement(t, 24)

    def getPressureCalibrationCoefficients(self):
        """Get pressure calibration coefficients from sensor.
        Returns:
            int: Pressure calibration coefficient (c00)
            int: Pressure calibration coefficient (c10)
            int: Pressure calibration coefficient (c20)
            int: Pressure calibration coefficient (c30)
            int: Pressure calibration coefficient (c01)
            int: Pressure calibration coefficient (c11)
            int: Pressure calibration coefficient (c21)
        """
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
        """
        Combines a list of bytes into a single integer and applies two's complement.
        Args:
            bytes_list (list of int): The list of bytes to be combined.
            length (int): The bit length for two's complement conversion.
        Returns:
            int: The combined integer after two's complement conversion.
        """
        combined = 0
        for i, byte in enumerate(bytes_list):
            combined |= byte << (8 * (len(bytes_list) - i - 1))
        return getTwosComplement(combined, length)

    def getTemperatureCalibrationCoefficients(self):
        """Get temperature calibration coefficients from sensor.
        Returns:
            int: Temperature calibration coefficient (c0)
            int: Temperature calibration coefficient (c1)
        """
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
        """Calculate scaled pressure.
        Returns:
            float: Scaled pressure
        """
        raw_p = self.getRawPressure()
        scaled_p = raw_p / self.kP
        return scaled_p

    def calcScaledTemperature(self):
        """Calculate scaled temperature.
        Returns:
            float: Scaled temperature
        """
        raw_t = self.getRawTemperature()
        scaled_t = raw_t / self.kT
        return scaled_t

    def calcCompTemperature(self, scaled_t):
        """Calculate compensated temperature.
        Args:
            scaled_t (float): Scaled temperature
        Returns:
            float: Compensated temperature [C]
        """
        c0, c1 = self.getTemperatureCalibrationCoefficients()
        comp_t = c0 * 0.5 + c1 * scaled_t
        return comp_t

    def calcCompPressure(self, scaled_p, scaled_t):
        """Calculate compensated pressure.
        Args:
            scaled_p (float): Scaled pressure
            scaled_t (float): Scaled temperature
        Returns:
            float: Compensated pressure [Pa]
        """
        c00, c10, c20, c30, c01, c11, c21 = self.getPressureCalibrationCoefficients()
        comp_p = (c00 + scaled_p * (c10 + scaled_p * (c20 + scaled_p * c30))
                + scaled_t * (c01 + scaled_p * (c11 + scaled_p * c21)))
        return comp_p

    def measureTemperatureOnce(self):   
        """Measures compensated temperature once.
        Returns:
            float: One compensated temperature value [C]
        """    
        t = self.calcScaledTemperature()
        temperature = self.calcCompTemperature(t)       
        return temperature
        
    def measurePressureOnce(self): 
        """Measure compensated pressure once.
        Returns:
            float:One Compensated pressure value [Pa]
        """       
        p = self.calcScaledPressure()
        t = self.calcScaledTemperature()
        pressure = self.calcCompPressure(p, t) 
        return pressure
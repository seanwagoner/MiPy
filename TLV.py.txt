import machine
import math
import time
from machine import I2C

class TLV493D:
    
    """Class of 3D Magnetic Sensor TLV493D.
    """
    
    def __init__(self):
        self.addr = 0x5e
        self.bx = 0
        self.by = 0
        self.bz = 0 
        self.temp = 0
        self.data = bytearray(10)
        self.bus = machine.I2C(0, scl='P6_0', sda='P6_1')
    
    def update_data(self):
        """ Read data from register
        """
        self.bus.writeto(self.addr, bytes([0x11, 0x01]))
        self.bus.readfrom_into(self.addr, self.data)
      
    def get_x(self):
        """ Get the value of X coordinate
            
            Returns:
            
            int: X coordinate
        """
        self.bx = (self.data[0] << 4) | ((self.data[4] >> 4) & 0x0f)
        
        if self.bx > 2047:
            self.bx -= 4096
        self.bx *= 0.098
            
        return self.bx
    
    def get_y(self):
        """ Get the value of Y coordinate
            
            Returns:
            
            int: Y coordinate
        """
        self.by = (self.data[1] << 4) | (self.data[4] & 0x0f)

        if self.by > 2047:
            self.by -= 4096
        self.by *= 0.098
            
        return self.by
    
    def get_z(self):
        """ Get the value of Z coordinate
            
            Returns:
            
            int: Z coordinate
        """
        self.bz = (self.data[2] << 4) | (self.data[5] & 0x0f)

        if self.bz > 2047:
            self.bz -= 4096
        self.bz *= 0.098
            
        return self.bz
    
    def get_br(self):
        """ Calculate the radial value
            
            Returns:
            
            double : radial value
        """
        br = math.sqrt(self.bx * self.bx + self.by * self.by + self.bz * self.bz)
        return br
    
    def get_polar(self):
        """ Calculate the polar value
            
            Returns:
            
            double: polar value
        """
        polar = math.cos(math.atan2(self.bz, math.sqrt(self.bx * self.bx + self.by * self.by)))
        return polar
    
    def get_azimuth(self):
        """ Calculate the azimuthal value
            
            Returns:
            
            double: azimuthal value
        """
        azimuth = math.atan2(self.by, self.bx)
        return azimuth

sensor = TLV493D()

while True:
    sensor.update_data()
    x = sensor.get_x()
    y = sensor.get_y()
    z = sensor.get_z()
    br = sensor.get_br()
    polar = sensor.get_polar()
    azimuth = sensor.get_azimuth()
    
    print("X:", x)
    print("Y:", y)
    print("Z:", z)
    print("BR:", br)
    print("Polar:", polar)
    print("Azimuth:", azimuth)
    
    time.sleep(1)

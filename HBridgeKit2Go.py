import machine
from machine import Pin, SPI

"""
    
    Author: Cole Costa
    Created on: 03/03/24
    
    These functions interface the Infineon PSoC6 with the HBridgeKit2Go.
    The kit includes the XMC1100 microcontroller which is used for SPI
    communication, as well as the IFX9201SG for 6A H-Bridge with SPI.
    This code assumes the usage of SPI Pins P9_0 for MOSI, P9_1 for MISO,
    P9_2 for SCK, and P9_3 for CS. The PSoC6 operates in master mode at
    a baudrate of 115200 bps. Refer to the Infineon IFX9201SG datasheet
    for more information on registers and their bits. This code is designed 
    for the control of DC motors or other inductive loads up to 6A.
    
"""

class HBridgeKit2Go:
    """
    Initializes SPI protocol, chip select, and the read and write buffers.
    """
    def __init__(self):
        self.spi = SPI(0, baudrate=115200, bits=8, firstbit=SPI.MSB, polarity=0, phase=1, sck='P9_2', mosi='P9_0', miso='P9_1')
        self.cs = Pin('P9_3', mode=Pin.OUT)
        self.writebuf = bytearray(1)
        self.readbuf = bytearray(1)
        print('')
    
    """
    This function is used to read and or write a command to the IFX9201SG
    via SPI using the XMC1100 on the kit.
    """
    def readWriteCMD(self, data):
        #buffer the data
        self.writebuf[0] = data
        
        #cs low active and write data
        self.cs.off()
        self.spi.write_readinto(self.writebuf, self.readbuf)
        self.cs.on()
        
        #cs low active and read data
        self.cs.off()
        self.spi.write_readinto(self.writebuf, self.readbuf)
        self.cs.on()
        
        #return read data unbuffered, can also be accessed by self.readbuf
        return self.readbuf[0]
    
    """
    This function enables control of the outputs via SPI by setting
    only the SIN bit in the Control Register.
    """
    def enableSPI(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x88
        self.readWriteCMD(ctrl)
        
    """
    This function disables control of the outputs via SPI by clearing
    only the SIN bit in the Control Register.
    """
    def disableSPI(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x80
        ctrl &= 0xF7
        self.readWriteCMD(ctrl)
    
    """
    This function clears only the SEN bit in the Control Register,
    which disables motor operation.
    """
    def disableOutput(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        #or the first bit to create a write cmd
        ctrl |= 0x80
        #and with a 0 to disable the output
        ctrl &= 0xFB
        self.readWriteCMD(ctrl)
    
    """
    This function sets only the SEN bit in the Control Register, which
    enables motor operation.
    """
    def enableOutput(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        #or the first bit to create a write cmd and or SEN to enable
        ctrl |= 0x84
        self.readWriteCMD(ctrl)
    
    """
    This function sets only the OLDIS bit in the Control Register, which
    disconnects the open load current source.
    """
    def disconnectOLCS(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x90
        self.readWriteCMD(ctrl)
    
    """
    This function clears only the OLDIS bit in the Control Register, which
    connects the open load current source.
    """
    def connectOLCS(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x80
        ctrl &= 0xEF
        self.readWriteCMD(ctrl)
    
    """
    This function toggles only the SDIR bit in the Control Register, which
    toggles the direction of the motor drive.
    """
    def toggleDIR(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        cmd = (ctrl & 0x02) >> 1
        if(cmd):
            ctrl |= 0x80
            self.readWriteCMD(ctrl & 0xFD)
        else:
            ctrl |= 0x80
            self.readWriteCMD(ctrl | 0x02)
    
    """
    This function enables PWM output by setting only the SPWM bit in the 
    Control Register.
    """
    def enablePWM(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x81
        self.readWriteCMD(ctrl)
        
    """
    This function disables PWM output by clearing only the SPWM bit in the 
    Control Register.
    """
    def disablePWM(self):
        #read the current CTRL Register
        ctrl = self.readCTRL()
        #create the new cmd
        ctrl |= 0x80
        ctrl &= 0xFE
        self.readWriteCMD(ctrl)
        
    """
    This function reads the Control Register, prints its hexidecimal value
    to the terminal, then returns the non hex value.
    """
    def readCTRL(self):
        #read the value using read CTRL cmd from datasheet
        ctrl = self.readWriteCMD(0x60)
        #print the hex value
        print(f'Control Register: {hex(ctrl)}')
        #return the non hex value
        return ctrl
    
    """
    This function reads the Diagnosis Register, prints its hexidecimal value
    to the terminal, then returns the non hex value.
    """
    def readDIA(self):
        #read the value using read DIA from datasheet
        dia = self.readWriteCMD(0x00)
        #print the hex value
        print(f'Diagnosis Register: {hex(dia)}')
        #return the non hex value
        return dia
    
    """
    This function resets the values in the Diagnosis Register, then calls
    the readDIA() function to verify the reset.
    """
    def resetDIA(self):
        #reset the DIA register using cmd from datasheet
        self.readWriteCMD(0x80)
        #read the DIA register
        self.readDIA()
    
    """
    This function reads the Revision Register, prints its hexidecimal value
    to the terminal, then returns its non hex value.
    """
    def readREV(self):
        #read the REV reg using cmd from datasheet
        rev = self.readWriteCMD(0x20)
        #print the hex value
        print(f'Revision Register: {hex(rev)}')
        #return the non hex value
        return rev
        






        

        

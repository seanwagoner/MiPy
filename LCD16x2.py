import machine
import time
from machine import I2C, Pin

""" 

    Author: Cole Costa
    Created on: 02/20/24
    
    These functions interface the Infineon PSoc6 with the 16x2
    Liquid Crystal Display using an I2C protocol with slave address
    0x27. This code also assumes usage of I2C pins P6_0 and P6_1
    for the SCL and SDA lines respectively. These fields can be
    changed by changing the self.addr for a different address
    and by using self.bus.init() to use different I2C pins.
    
"""

class LCD16x2:
    
    def __init__(self):
        self.addr = 0x27
        self.bus = I2C(0, scl='P6_0', sda='P6_1', freq=100000)
        
    def LCD_writeINSTR(self, data):
        self.bus.writeto(self.addr, bytes([(data & 0xF0) | 0x0C, (data & 0xF0) | 0x08, 
        ((data & 0x0F) << 4) | 0x0C, ((data & 0x0F) << 4) | 0x08]))
        
    def LCD_writeDATA(self, data):
        self.bus.writeto(self.addr, bytes([(data & 0xF0) | 0x0D, (data & 0xF0) | 0x09, 
        ((data & 0x0F) << 4) | 0x0D, ((data & 0x0F) << 4) | 0x09]))
        
    def LCD_INIT(self):
        """
        Initialization sequence for the LCD as per datasheet
        """
    
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x30)
        
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x30)
        
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x30)
        
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x20)
        
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x28)
        
        time.sleep_ms(40)
        self.LCD_writeINSTR(0x00)
        
        time.sleep_ms(40)
        
    def LCD_writeString(self, string):
        if len(string) > 40:
            print("Input string is greater than max length of 40.")
        else:
            for i in range(len(string)):
                self.LCD_writeDATA(ord(string[i]))
            
    def LCD_clearDisplay(self):
        """
        Clears the display, turns on the display, and resets cursor
        """
        self.LCD_writeINSTR(0x01)
        self.LCD_writeINSTR(0x0F)
        self.LCD_writeINSTR(0x80)
            
    def LCD_replaceCursor(self):
        """
        Puts Cursor at position 0,0
        """
        self.LCD_writeINSTR(0x80)
        
    def LCD_putCursor(self, row, col):
        """
        First Row is 0, second Row is 1
        First Col is 0, last Col is 15
        """
        if(row == 0):
            col |= 0x80
        else:
            col |= 0xC0
        self.LCD_writeINSTR(col)
        
    def LCD_shiftRight(self):
        """
        Shifts the entire display to the right once
        """
        self.LCD_writeINSTR(0x1C)
    
    def LCD_shiftLeft(self):
        """
        Shifts the entire display to the left once
        """
        self.LCD_writeINSTR(0x18)
        
    def LCD_cursorOff(self):
        """
        Removes the cursor position character from the screen
        """
        self.LCD_writeINSTR(0x0C)
    
    def LCD_cursorOn(self):
        """
        Turns the cursor on with blinking
        """
        self.LCD_writeINSTR(0x0F)
        
    def LCD_cursorNoBlink(self):
        """
        Turns the Cursor on with no blinking
        """
        self.LCD_writeINSTR(0x0E)
        
    def LCD_displayOff(self):
        """
        Turns off the Display
        """
        self.LCD_writeINSTR(0x08)
        
    def LCD_displayOn(self):
        """
        Turns on the Display with the cursor and blinking
        """
        self.LCD_writeINSTR(0x0F)
        
    def LCD_rotateDisplayRight(self):
        """
        Rotates the Display to the right indefinitely with a half
        second delay between rotations
        NOTE: This function does not return
        """
        while True:
            self.LCD_writeINSTR(0x1C)
            time.sleep_ms(500)
    
    def LCD_rotateDisplayLeft(self):
        """
        Rotates the Display to the left indefinitely with a half
        second delay between rotations
        NOTE: This function does not return
        """
        while True:
            self.LCD_writeINSTR(0x18)
            time.sleep_ms(500)
        
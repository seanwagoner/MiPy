import time, machine
from machine import Pin

class HCSR04:
    """
    Driver to use the untrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    """
    # echo_timeout_us is based in chip range limit (400cm)
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin.
        By default is based in sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT)
        self.trigger.value(0)
        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN)

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.trigger.value(0)
        
        pulse_time = self.time_pulse_us(self.echo, 1, self.echo_timeout_us)
        while(pulse_time == -1 and pulse_time == -2):
            pulse_time = self.time_pulse_us(self.echo, 1, self.echo_timeout_us)

        return pulse_time

    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms
        
    def time_pulse_us(self, echo_pin, pulse_level, timeout_us):
        """
        Times the pulse on the given echo_pin and returns the duration of the pulse
        in microseconds. pulse_level is 0 or 1 for low or high to be detected. 
        returns -1 if there is a timeout_us in the main measurement and -2 if there is
        a timeout in the pulse check measurement
        """
        start = time.ticks_us()
        while(echo_pin.value() != pulse_level):
            if((time.ticks_us() - start) >= timeout_us):
                return -2
        
        start = time.ticks_us()
        while(echo_pin.value() == pulse_level):
            if((time.ticks_us() - start) >= timeout_us):
                return -1
                
        return time.ticks_us() - start
        
        
sensor = HCSR04('P6_0', 'P6_1')
while(1):
    print(sensor.distance_cm())
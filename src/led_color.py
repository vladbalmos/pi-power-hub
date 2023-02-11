from machine import PWM

class LEDColor:
    
    def __init__(self, pin, initial_value = 0, max_value = 255):
        self._pin = pin
        self._freq = 1000
        self._pwm = PWM(pin)
        self._max_value = max_value
        
        if initial_value > max_value:
            initial_value = max_value

        self._value = initial_value
        self._pwm.duty_u16(self._value ** 2)
    
    def value(self, v):
        if v > self._max_value:
            v = self._max_value

        self._value = v
        self._pwm.duty_u16(self._value ** 2)
    
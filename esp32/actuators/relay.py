from machine import Pin


class Relay:
    def __init__(self, pin_number, active_low=True):
        self.active_low = active_low
        self.pin = Pin(pin_number, Pin.OUT)

        self.off()

    def on(self):
        if self.active_low:
            self.pin.value(0)
        else:
            self.pin.value(1)

    def off(self):
        if self.active_low:
            self.pin.value(1)
        else:
            self.pin.value(0)

    def is_on(self):
        value = self.pin.value()

        if self.active_low:
            return value == 0

        return value == 1
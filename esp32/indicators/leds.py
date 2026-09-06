from machine import Pin


class StatusLeds:
    def __init__(self, green_pin, red_pin):
        self.green = Pin(green_pin, Pin.OUT)
        self.red = Pin(red_pin, Pin.OUT)

        self.off()

    def green_on(self):
        self.green.on()
        self.red.off()

    def red_on(self):
        self.green.off()
        self.red.on()

    def off(self):
        self.green.off()
        self.red.off()

    def update_from_temperature(self, temperature, threshold=30):
        if temperature < threshold:
            self.green_on()
            return "NORMAL"

        self.red_on()
        return "HOT"

    def update_from_humidity(self, humidity, threshold=75):
            if humidity > threshold:
                self.green_on()
                return "NORMAL"
            self.off
            self.red_on()
            return "DRY"
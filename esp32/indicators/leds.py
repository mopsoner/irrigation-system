from machine import Pin


class StatusLeds:
    def __init__(self, green_pin, yellow_pin, red_pin):
        self.green = Pin(green_pin, Pin.OUT)
        self.yellow = Pin(yellow_pin, Pin.OUT)
        self.red = Pin(red_pin, Pin.OUT)

        self.off()

    def green_on(self):
        self.green.on()
        self.yellow.off()
        self.red.off()

    def yellow_on(self):
        self.green.off()
        self.yellow.on()
        self.red.off()

    def red_on(self):
        self.green.off()
        self.yellow.off()
        self.red.on()

    def off(self):
        self.green.off()
        self.yellow.off()
        self.red.off()

    def update(self, temperature, humidity, temp_threshold=30, hum_threshold=75):
        temperature_ok = temperature < temp_threshold
        humidity_ok = humidity > hum_threshold

        if temperature_ok and humidity_ok:
            self.green_on()
        elif temperature_ok != humidity_ok:
            self.yellow_on()
        else:
            self.red_on()

        return (
            "NORMAL" if temperature_ok else "HOT",
            "NORMAL" if humidity_ok else "DRY"
        )

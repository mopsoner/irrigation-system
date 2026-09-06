from machine import Pin
import dht
import time


class DHTSensor:
    def __init__(self, pin_number=13):
        self.sensor = dht.DHT11(Pin(pin_number))

    def read(self):
        self.sensor.measure()

        return {
            "temperature": self.sensor.temperature(),
            "humidity": self.sensor.humidity()
        }
from time import sleep

from sensors.dht_sensor import DHTSensor
from indicators.leds import StatusLeds


TEMP_THRESHOLD = 30

HUM_THRESHOLD = 75


sensor = DHTSensor(pin_number=27)

leds = StatusLeds(
    green_pin=15,
    red_pin=21
)

print("================================")
print(" Irrigation ESP32 Controller")
print(" Temperature monitoring")
print(" Threshold: {} C".format(TEMP_THRESHOLD))
print("================================")


while True:
    try:
        data = sensor.read()

        temperature = data["temperature"]
        humidity = data["humidity"]

        statusTemperature = leds.update_from_temperature(
            temperature,
            TEMP_THRESHOLD
        )

        statusHumidity= leds.update_from_humidity(
            humidity,
            HUM_THRESHOLD
        )

        print(
            "Temperature: {} C | Humidity: {} % | Status: {}".format(
                temperature,
                humidity,
                statusTemperature+" / "+statusHumidity
            )
        )

    except Exception as error:
        print("DHT11 error:", error)
        leds.off()

    sleep(3)
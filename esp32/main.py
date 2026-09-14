from time import sleep

from sensors.dht_sensor import DHTSensor
from indicators.leds import StatusLeds
from indicators.lcd1602 import LCD1602


TEMP_THRESHOLD = 30

HUM_THRESHOLD = 75


sensor = DHTSensor(pin_number=27)

lcd = LCD1602(
    sda_pin=21,
    scl_pin=22
)

leds = StatusLeds(
    green_pin=15,
    yellow_pin=2,
    red_pin=4
)


lcd = None

try:
    lcd = LCD1602(
        sda_pin=32,
        scl_pin=33
    )
    print("LCD1602 detected at address", hex(lcd.address))
except Exception as error:
    # L'arrosage et les LED doivent continuer meme si l'ecran est absent.
    print("LCD1602 error:", error)


def display_message(first_line, second_line):
    if lcd is None:
        return

    try:
        lcd.write_lines(first_line, second_line)
    except Exception as error:
        # Une panne I2C ne doit pas etre confondue avec une panne du DHT11.
        print("LCD1602 write error:", error)


print("================================")

display_message(
    "Irrigation",
    "Demarrage..."
)
print(" Irrigation ESP32 Controller")
print(" Temperature monitoring")
print(" Threshold: {} C".format(TEMP_THRESHOLD))
print("================================")


while True:
    try:
        data = sensor.read()

        temperature = data["temperature"]
        humidity = data["humidity"]

        status_temperature, status_humidity = leds.update(
            temperature,
            humidity,
            TEMP_THRESHOLD,
            HUM_THRESHOLD
        )

        print(
            "Temperature: {} C | Humidity: {} % | Status: {}".format(
                temperature,
                humidity,
                status_temperature + " / " + status_humidity
            )
        )

        display_message(
            "T:{}C H:{}%".format(temperature, humidity),
            "{} / {}".format(status_temperature, status_humidity)
        )

    except Exception as error:
        print("DHT11 error:", error)
        leds.off()
        display_message(
            "Erreur capteur",
            "Verifier DHT11"
        )

    sleep(3)

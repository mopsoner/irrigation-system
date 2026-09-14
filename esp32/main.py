from time import sleep

from sensors.dht_sensor import DHTSensor
from sensors.motion_sensor import MotionSensor
from indicators.leds import StatusLeds
from indicators.lcd1602 import LCD1602
from indicators.buzzer import StateChangeBuzzer


TEMP_THRESHOLD = 30

HUM_THRESHOLD = 75

# Cablage LCD1602 du tutoriel Freenove FNK0025. GPIO 34/35 sont des entrees
# uniquement sur l'ESP32 classique et ne peuvent pas servir de SDA/SCL.
LCD_SDA_PIN = 13
LCD_SCL_PIN = 14
MOTION_SENSOR_PIN = 35
BUZZER_PIN = 12


sensor = DHTSensor(pin_number=27)
motion_sensor = MotionSensor(pin_number=MOTION_SENSOR_PIN)
buzzer = StateChangeBuzzer(pin_number=BUZZER_PIN)

leds = StatusLeds(
    green_pin=15,
    yellow_pin=2,
    red_pin=4
)

# Keep a visible indicator on while the first sensor measurement is pending.
leds.yellow_on()

lcd = None

try:
    lcd = LCD1602(
        sda_pin=LCD_SDA_PIN,
        scl_pin=LCD_SCL_PIN
    )
    print("LCD1602 detected at address", hex(lcd.address))
except Exception as error:
    # La surveillance continue meme si l'ecran est absent ou debranche.
    print("LCD1602 error:", error)


def display_message(first_line, second_line):
    if lcd is None:
        return

    try:
        lcd.write_lines(first_line, second_line)
    except Exception as error:
        # Une panne I2C ne doit pas interrompre la lecture du DHT11.
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
        motion_detected = motion_sensor.motion_detected()

        status_temperature, status_humidity = leds.update(
            temperature,
            humidity,
            TEMP_THRESHOLD,
            HUM_THRESHOLD
        )

        buzzer.notify_state((
            status_temperature,
            status_humidity,
            motion_detected,
        ))

        print(
            "Temperature: {} C | Humidity: {} % | Motion: {} | Status: {}".format(
                temperature,
                humidity,
                "DETECTED" if motion_detected else "NONE",
                status_temperature + " / " + status_humidity
            )
        )

        display_message(
            "T:{}C H:{}%".format(temperature, humidity),
            "T:{} H:{} M:{}".format(
                status_temperature[0],
                status_humidity[0],
                "OUI" if motion_detected else "NON",
            )
        )

    except Exception as error:
        print("Sensor error:", error)
        # A sensor failure must be visible instead of leaving every LED off.
        leds.red_on()
        buzzer.notify_state(("ERROR",))
        display_message(
            "Erreur capteur",
            "Verifier capteurs"
        )

    sleep(3)

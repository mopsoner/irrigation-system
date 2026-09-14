from time import sleep

from sensors.dht_sensor import DHTSensor
from sensors.motion_sensor import MotionSensor
from indicators.leds import StatusLeds
from indicators.lcd1602 import LCD1602
from indicators.buzzer import StateChangeBuzzer
from connectivity.wifi import WiFi
from cameras.ov2640 import OV2640Camera
from wifi_config import WIFI_CONNECTION_TIMEOUT_MS, WIFI_PASSWORD, WIFI_SSID


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


def initialize_camera():
    try:
        camera = OV2640Camera()
        print("OV2640 camera ready")
        return camera
    except Exception as error:
        # Le controle des capteurs reste operationnel avec un firmware sans
        # module camera ou lorsque l'OV2640 est debranche.
        print("OV2640 camera error:", error)
        return None


def initialize_wifi():
    wifi = WiFi()

    try:
        networks = wifi.scan()
        print("Wi-Fi networks found:", len(networks))
        for access_point in networks:
            name = access_point["ssid"] or "<hidden>"
            print(
                " - {} | channel {} | {} dBm | security {}".format(
                    name,
                    access_point["channel"],
                    access_point["rssi"],
                    access_point["security"],
                )
            )

        if WIFI_SSID:
            ip_config = wifi.connect(
                WIFI_SSID,
                WIFI_PASSWORD,
                timeout_ms=WIFI_CONNECTION_TIMEOUT_MS,
            )
            print("Wi-Fi connected to '{}' | IP: {}".format(WIFI_SSID, ip_config[0]))
        else:
            print("Wi-Fi scan only: configure WIFI_SSID in wifi_config.py to connect")
    except Exception as error:
        # La surveillance des capteurs doit rester disponible hors connexion.
        print("Wi-Fi error:", error)

    return wifi


wifi = initialize_wifi()
camera = initialize_camera()

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

motion_was_detected = False
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
        photo_path = None

        # Une detection correspond au front montant du PIR. Tant que sa sortie
        # reste haute, une seule photo est donc prise.
        if motion_detected and not motion_was_detected and camera is not None:
            try:
                photo_path = camera.capture()
                print("Photo captured:", photo_path)
            except Exception as error:
                # Une erreur camera ne doit pas masquer les mesures DHT/PIR.
                print("OV2640 capture error:", error)
        motion_was_detected = motion_detected

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

        if photo_path:
            display_message(
                "Photo prise !",
                photo_path.split("/")[-1],
            )
        else:
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

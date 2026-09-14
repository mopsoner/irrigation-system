from time import sleep_ms, ticks_diff, ticks_ms

from sensors.dht_sensor import DHTSensor
from sensors.motion_sensor import MotionActivationTracker, MotionSensor
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
PIR_POLL_INTERVAL_MS = 100
DHT_READ_INTERVAL_MS = 3000


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

motion_tracker = MotionActivationTracker()
if motion_sensor.on_rising(motion_tracker.notify_rising):
    print("PIR rising-edge interrupt enabled")
else:
    print("PIR interrupt unavailable; using fast polling")

display_message(
    "Irrigation",
    "Demarrage..."
)
print(" Irrigation ESP32 Controller")
print(" Temperature monitoring")
print(" Threshold: {} C".format(TEMP_THRESHOLD))
print("================================")


last_dht_read_ms = ticks_ms() - DHT_READ_INTERVAL_MS
last_temperature = None
last_humidity = None
last_temperature_status = "WAIT"
last_humidity_status = "WAIT"

while True:
    motion_detected = motion_sensor.motion_detected()
    photo_path = None

    # L'IRQ ne fait que poser un indicateur. La capture et l'ecriture du
    # fichier restent dans la boucle principale. Le sondage rapide observe
    # aussi sans delai le retour a l'etat bas et sert de repli sans IRQ.
    if motion_tracker.update(motion_detected) and camera is not None:
        try:
            photo_path = camera.capture()
            print("Photo captured:", photo_path)
        except Exception as error:
            print("OV2640 capture error:", error)

    try:
        now = ticks_ms()
        if ticks_diff(now, last_dht_read_ms) < DHT_READ_INTERVAL_MS:
            if photo_path:
                display_message("Photo prise !", photo_path.split("/")[-1])
            sleep_ms(PIR_POLL_INTERVAL_MS)
            continue

        last_dht_read_ms = now
        data = sensor.read()
        last_temperature = data["temperature"]
        last_humidity = data["humidity"]

        last_temperature_status, last_humidity_status = leds.update(
            last_temperature,
            last_humidity,
            TEMP_THRESHOLD,
            HUM_THRESHOLD
        )

        buzzer.notify_state((
            last_temperature_status,
            last_humidity_status,
            motion_detected,
        ))

        print(
            "Temperature: {} C | Humidity: {} % | Motion: {} | Status: {}".format(
                last_temperature,
                last_humidity,
                "DETECTED" if motion_detected else "NONE",
                last_temperature_status + " / " + last_humidity_status
            )
        )

        if photo_path:
            display_message(
                "Photo prise !",
                photo_path.split("/")[-1],
            )
        else:
            display_message(
                "T:{}C H:{}%".format(last_temperature, last_humidity),
                "T:{} H:{} M:{}".format(
                    last_temperature_status[0],
                    last_humidity_status[0],
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

    sleep_ms(PIR_POLL_INTERVAL_MS)

import importlib
import pathlib
import sys
import time
import types
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))


class FakePin:
    def __init__(self, number):
        self.number = number


class FakeSoftI2C:
    devices = [0x27]

    def __init__(self, *, sda, scl, freq):
        self.sda = sda
        self.scl = scl
        self.freq = freq
        self.writes = []

    def scan(self):
        return self.devices

    def writeto(self, address, data):
        self.writes.append((address, bytes(data)))


fake_machine = types.ModuleType("machine")
fake_machine.Pin = FakePin
fake_machine.SoftI2C = FakeSoftI2C
sys.modules["machine"] = fake_machine
time.sleep_ms = lambda milliseconds: None

lcd_module = importlib.import_module("indicators.lcd1602")


class LCD1602Tests(unittest.TestCase):
    def test_uses_soft_i2c_on_freenove_pins_and_detects_lcd(self):
        with patch.object(lcd_module, "sleep_ms"):
            lcd = lcd_module.LCD1602()

        self.assertEqual(lcd.i2c.sda.number, 13)
        self.assertEqual(lcd.i2c.scl.number, 14)
        self.assertEqual(lcd.i2c.freq, 100000)
        self.assertEqual(lcd.address, 0x27)
        self.assertTrue(lcd.i2c.writes)

    def test_does_not_select_an_unrelated_i2c_device(self):
        bus = FakeSoftI2C(
            sda=FakePin(34),
            scl=FakePin(35),
            freq=100000,
        )
        bus.devices = [0x40]

        with self.assertRaisesRegex(OSError, r"scan=\['0x40'\]"):
            lcd_module.LCD1602(i2c=bus)

    def test_writes_two_padded_lines(self):
        bus = FakeSoftI2C(
            sda=FakePin(34),
            scl=FakePin(35),
            freq=100000,
        )
        with patch.object(lcd_module, "sleep_ms"):
            lcd = lcd_module.LCD1602(i2c=bus)
            writes_before = len(bus.writes)
            lcd.write_lines("Irrigation", "Demarrage...")

        # Deux curseurs et 32 caracteres, six transferts PCF8574 par octet.
        self.assertEqual(len(bus.writes) - writes_before, 204)

    def test_pads_and_truncates_lines_without_ljust(self):
        bus = FakeSoftI2C(
            sda=FakePin(34),
            scl=FakePin(35),
            freq=100000,
        )
        with patch.object(lcd_module, "sleep_ms"):
            lcd = lcd_module.LCD1602(i2c=bus)

        written = []
        lcd.set_cursor = lambda column, row: None
        lcd.write = written.append

        lcd.write_lines(29, "abcdefghijklmnopq")

        self.assertEqual(written, ["29" + " " * 14, "abcdefghijklmnop"])


if __name__ == "__main__":
    unittest.main()

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
    OUT = 1

    def __init__(self, number, mode):
        self.number = number
        self.mode = mode
        self.values = []

    def value(self, value=None):
        if value is None:
            return self.values[-1]
        self.values.append(value)


fake_machine = types.ModuleType("machine")
fake_machine.Pin = FakePin
sys.modules["machine"] = fake_machine
time.sleep_ms = lambda milliseconds: None

buzzer_module = importlib.import_module("indicators.buzzer")


class StateChangeBuzzerTests(unittest.TestCase):
    def test_uses_gpio_12_and_starts_silent(self):
        buzzer = buzzer_module.StateChangeBuzzer()

        self.assertEqual(buzzer.pin.number, 12)
        self.assertEqual(buzzer.pin.mode, FakePin.OUT)
        self.assertEqual(buzzer.pin.values, [0])

    def test_beeps_only_when_state_changes(self):
        buzzer = buzzer_module.StateChangeBuzzer(beep_duration_ms=75)

        with patch.object(buzzer_module, "sleep_ms") as sleep:
            self.assertFalse(buzzer.notify_state(("NORMAL", "NORMAL", False)))
            self.assertFalse(buzzer.notify_state(("NORMAL", "NORMAL", False)))
            self.assertTrue(buzzer.notify_state(("HOT", "NORMAL", False)))

        sleep.assert_called_once_with(75)
        self.assertEqual(buzzer.pin.values, [0, 1, 0])

    def test_can_drive_an_active_low_buzzer(self):
        buzzer = buzzer_module.StateChangeBuzzer(active_high=False)

        buzzer.beep()

        self.assertEqual(buzzer.pin.values, [1, 0, 1])


if __name__ == "__main__":
    unittest.main()

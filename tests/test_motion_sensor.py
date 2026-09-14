import importlib
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))


class FakePin:
    IN = 0

    def __init__(self, number, mode):
        self.number = number
        self.mode = mode
        self.state = 0

    def value(self):
        return self.state


fake_machine = types.ModuleType("machine")
fake_machine.Pin = FakePin
sys.modules["machine"] = fake_machine

motion_sensor_module = importlib.import_module("sensors.motion_sensor")


class MotionSensorTests(unittest.TestCase):
    def test_uses_gpio_35_as_an_input_by_default(self):
        sensor = motion_sensor_module.MotionSensor()

        self.assertEqual(sensor.pin.number, 35)
        self.assertEqual(sensor.pin.mode, FakePin.IN)

    def test_reports_motion_from_a_high_signal(self):
        sensor = motion_sensor_module.MotionSensor()

        self.assertFalse(sensor.motion_detected())
        sensor.pin.state = 1
        self.assertTrue(sensor.motion_detected())


if __name__ == "__main__":
    unittest.main()

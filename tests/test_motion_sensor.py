import importlib
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))


class FakePin:
    IN = 0
    IRQ_RISING = 1

    def __init__(self, number, mode):
        self.number = number
        self.mode = mode
        self.state = 0
        self.irq_trigger = None
        self.irq_handler = None

    def value(self):
        return self.state

    def irq(self, trigger, handler):
        self.irq_trigger = trigger
        self.irq_handler = handler


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

    def test_configures_a_rising_edge_interrupt(self):
        sensor = motion_sensor_module.MotionSensor()
        callback = lambda pin: None

        self.assertTrue(sensor.on_rising(callback))
        self.assertEqual(sensor.pin.irq_trigger, FakePin.IRQ_RISING)
        self.assertIs(sensor.pin.irq_handler, callback)


class MotionActivationTrackerTests(unittest.TestCase):
    def setUp(self):
        self.tracker = motion_sensor_module.MotionActivationTracker()

    def test_catches_a_pir_pulse_shorter_than_the_dht_interval(self):
        self.tracker.notify_rising()

        # Au prochain sondage le signal est deja redescendu, mais le front IRQ
        # memorise doit tout de meme provoquer une capture.
        self.assertTrue(self.tracker.update(False))
        self.assertFalse(self.tracker.update(False))

    def test_rearms_after_the_signal_returns_low(self):
        self.assertTrue(self.tracker.update(True))
        self.assertFalse(self.tracker.update(False))
        self.assertTrue(self.tracker.update(True))

    def test_does_not_capture_repeatedly_while_signal_stays_high(self):
        self.assertTrue(self.tracker.update(True))
        self.assertFalse(self.tracker.update(True))
        self.assertFalse(self.tracker.update(True))


if __name__ == "__main__":
    unittest.main()

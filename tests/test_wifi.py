import importlib
import pathlib
import sys
import time
import types
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))


class FakeWLAN:
    def __init__(self):
        self.enabled = False
        self.connected = False
        self.connect_args = None
        self.disconnected = False
        self.scan_results = []
        self.connection_status = 1

    def active(self, enabled=None):
        if enabled is not None:
            self.enabled = enabled
        return self.enabled

    def scan(self):
        return self.scan_results

    def connect(self, ssid, password):
        self.connect_args = (ssid, password)

    def disconnect(self):
        self.connected = False
        self.disconnected = True

    def isconnected(self):
        return self.connected

    def status(self):
        return self.connection_status

    def ifconfig(self):
        return ("192.168.1.24", "255.255.255.0", "192.168.1.1", "8.8.8.8")


fake_network = types.ModuleType("network")
fake_network.STA_IF = 0
fake_network.WLAN = lambda interface: FakeWLAN()
sys.modules["network"] = fake_network
time.sleep_ms = lambda milliseconds: None

wifi_module = importlib.import_module("connectivity.wifi")


class WiFiTests(unittest.TestCase):
    def test_scans_in_station_mode_and_sorts_by_signal(self):
        wlan = FakeWLAN()
        wlan.scan_results = [
            (b"potager", b"\x01" * 6, 6, -72, 3, 0),
            (b"serre", b"\x02" * 6, 11, -41, 4, 0),
        ]

        networks = wifi_module.WiFi(wlan=wlan).scan()

        self.assertTrue(wlan.enabled)
        self.assertEqual([item["ssid"] for item in networks], ["serre", "potager"])
        self.assertEqual(networks[0]["rssi"], -41)

    def test_connects_with_the_configured_credentials(self):
        wlan = FakeWLAN()
        wifi = wifi_module.WiFi(wlan=wlan)

        with patch.object(wifi_module, "sleep_ms", side_effect=lambda delay: setattr(wlan, "connected", True)):
            ip_config = wifi.connect("potager", "secret", timeout_ms=500)

        self.assertEqual(wlan.connect_args, ("potager", "secret"))
        self.assertEqual(ip_config[0], "192.168.1.24")

    def test_rejects_an_empty_ssid(self):
        with self.assertRaisesRegex(ValueError, "SSID"):
            wifi_module.WiFi(wlan=FakeWLAN()).connect(None, "secret")

    def test_stops_waiting_after_the_timeout(self):
        wlan = FakeWLAN()

        with patch.object(wifi_module, "sleep_ms"):
            with self.assertRaisesRegex(OSError, "Delai"):
                wifi_module.WiFi(wlan=wlan).connect(
                    "absent", "secret", timeout_ms=500, poll_interval_ms=250
                )

        self.assertTrue(wlan.disconnected)


if __name__ == "__main__":
    unittest.main()

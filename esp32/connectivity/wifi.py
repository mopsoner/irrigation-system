from time import sleep_ms

import network


class WiFi:
    """Gere le Wi-Fi de l'ESP32 en mode station (STA)."""

    def __init__(self, wlan=None):
        self.wlan = wlan or network.WLAN(network.STA_IF)

    @staticmethod
    def _decode_ssid(ssid):
        if isinstance(ssid, bytes):
            try:
                return ssid.decode("utf-8")
            except UnicodeError:
                return repr(ssid)
        return str(ssid)

    def scan(self):
        """Active la station et retourne les reseaux visibles, tries par signal."""
        self.wlan.active(True)
        networks = []

        for ssid, bssid, channel, rssi, security, hidden in self.wlan.scan():
            networks.append({
                "ssid": self._decode_ssid(ssid),
                "bssid": bssid,
                "channel": channel,
                "rssi": rssi,
                "security": security,
                "hidden": bool(hidden),
            })

        networks.sort(key=lambda item: item["rssi"], reverse=True)
        return networks

    def connect(self, ssid, password, timeout_ms=15000, poll_interval_ms=250):
        """Se connecte au reseau indique et retourne la configuration IP."""
        if not ssid:
            raise ValueError("Le SSID Wi-Fi est obligatoire")

        self.wlan.active(True)
        if self.wlan.isconnected():
            self.wlan.disconnect()

        self.wlan.connect(ssid, password or "")
        waited_ms = 0

        while not self.wlan.isconnected() and waited_ms < timeout_ms:
            status = self.wlan.status()
            if status < 0:
                raise OSError("Connexion Wi-Fi refusee (statut {})".format(status))
            sleep_ms(poll_interval_ms)
            waited_ms += poll_interval_ms

        if not self.wlan.isconnected():
            self.wlan.disconnect()
            raise OSError("Delai de connexion Wi-Fi depasse pour '{}'".format(ssid))

        return self.wlan.ifconfig()

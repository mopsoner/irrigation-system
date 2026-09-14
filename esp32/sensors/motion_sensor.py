from machine import Pin


class MotionSensor:
    """Lit la sortie numerique d'un detecteur de mouvement infrarouge."""

    def __init__(self, pin_number=35):
        # Le GPIO 35 de l'ESP32 est une entree uniquement et ne fournit pas
        # de resistance de tirage interne. Le module PIR fournit directement
        # un niveau logique, il doit donc etre configure en entree simple.
        self.pin = Pin(pin_number, Pin.IN)

    def motion_detected(self):
        """Retourne True lorsque le module PIR signale un mouvement."""
        return self.pin.value() == 1

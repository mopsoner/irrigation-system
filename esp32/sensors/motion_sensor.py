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

    def on_rising(self, callback):
        """Active l'interruption de front montant lorsqu'elle est disponible."""
        irq = getattr(self.pin, "irq", None)
        rising = getattr(Pin, "IRQ_RISING", None)
        if irq is None or rising is None:
            return False

        try:
            irq(trigger=rising, handler=callback)
        except (AttributeError, TypeError, ValueError):
            # Certains ports exposent Pin.irq sans prendre en charge ce GPIO.
            return False
        return True


class MotionActivationTracker:
    """Detecte une activation PIR unique, y compris entre deux lectures."""

    def __init__(self):
        self._active = False
        self._rising_pending = False

    def notify_rising(self, _pin=None):
        """Memorise un front; cette methode est sure pour un gestionnaire IRQ."""
        self._rising_pending = True

    def update(self, signal_is_high):
        """Retourne True une seule fois par activation, puis rearme a l'etat bas."""
        signal_is_high = bool(signal_is_high)
        activated = (self._rising_pending or signal_is_high) and not self._active
        self._rising_pending = False
        self._active = signal_is_high
        return activated

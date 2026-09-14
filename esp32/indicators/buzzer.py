from machine import Pin
from time import sleep_ms


class StateChangeBuzzer:
    """Emit a short beep whenever the monitored application state changes."""

    def __init__(self, pin_number=12, beep_duration_ms=100, active_high=True):
        self.pin = Pin(pin_number, Pin.OUT)
        self.beep_duration_ms = beep_duration_ms
        self.active_value = 1 if active_high else 0
        self.inactive_value = 0 if active_high else 1
        self.previous_state = None

        self.pin.value(self.inactive_value)

    def beep(self):
        self.pin.value(self.active_value)
        sleep_ms(self.beep_duration_ms)
        self.pin.value(self.inactive_value)

    def notify_state(self, state):
        """Remember the first state, then beep once for each transition."""
        if self.previous_state is None:
            self.previous_state = state
            return False

        if state == self.previous_state:
            return False

        self.previous_state = state
        self.beep()
        return True

from time import sleep_ms

from machine import I2C, Pin


class LCD1602:
    """Pilote d'un LCD1602 equipe d'un adaptateur I2C PCF8574."""

    _CLEAR = 0x01
    _ENTRY_MODE = 0x06
    _DISPLAY_ON = 0x0C
    _FUNCTION_2_LINES = 0x28

    _ENABLE = 0x04
    _BACKLIGHT = 0x08
    _RS = 0x01

    def __init__(self, sda_pin=21, scl_pin=22, i2c_id=0, address=None):
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.i2c = I2C(
            i2c_id,
            sda=Pin(sda_pin),
            scl=Pin(scl_pin),
            freq=100000
        )
        self.address = self._find_address() if address is None else address
        self._initialize()

    def _find_address(self):
        devices = self.i2c.scan()

        for address in (0x27, 0x3F):
            if address in devices:
                return address

        if devices:
            return devices[0]

        raise OSError(
            "Aucun LCD I2C detecte sur SDA {} / SCL {}".format(
                self.sda_pin,
                self.scl_pin
            )
        )

    def _write_expander(self, value):
        self.i2c.writeto(self.address, bytes((value | self._BACKLIGHT,)))

    def _pulse_enable(self, value):
        self._write_expander(value | self._ENABLE)
        sleep_ms(1)
        self._write_expander(value & ~self._ENABLE)
        sleep_ms(1)

    def _write_nibble(self, nibble, mode=0):
        value = (nibble & 0x0F) << 4 | mode
        self._write_expander(value)
        self._pulse_enable(value)

    def _send(self, value, mode=0):
        self._write_nibble(value >> 4, mode)
        self._write_nibble(value, mode)

    def _command(self, value):
        self._send(value)

        if value == self._CLEAR:
            sleep_ms(2)

    def _initialize(self):
        sleep_ms(50)

        # Sequence imposee par le HD44780 pour passer en mode 4 bits.
        self._write_nibble(0x03)
        sleep_ms(5)
        self._write_nibble(0x03)
        sleep_ms(1)
        self._write_nibble(0x03)
        self._write_nibble(0x02)

        self._command(self._FUNCTION_2_LINES)
        self._command(self._DISPLAY_ON)
        self._command(self._CLEAR)
        self._command(self._ENTRY_MODE)

    def set_cursor(self, column, row):
        if row not in (0, 1):
            raise ValueError("La ligne doit etre 0 ou 1")
        if not 0 <= column < 16:
            raise ValueError("La colonne doit etre comprise entre 0 et 15")

        self._command(0x80 | ((0x00, 0x40)[row] + column))

    def write(self, message):
        for character in str(message):
            self._send(ord(character), self._RS)

    def write_lines(self, first_line="", second_line=""):
        """Ecrit les deux lignes, tronquees ou completees a 16 caracteres."""
        for row, line in enumerate((first_line, second_line)):
            self.set_cursor(0, row)
            self.write(str(line)[:16].ljust(16))

    def clear(self):
        self._command(self._CLEAR)

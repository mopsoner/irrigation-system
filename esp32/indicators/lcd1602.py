from time import sleep_ms

import machine


class LCD1602:
    """Pilote un LCD1602 equipe d'un adaptateur I2C PCF8574."""

    _CLEAR = 0x01
    _ENTRY_MODE = 0x06
    _DISPLAY_ON = 0x0C
    _FUNCTION_2_LINES = 0x28

    _ENABLE = 0x04
    _BACKLIGHT = 0x08
    _RS = 0x01

    def __init__(self, sda_pin=13, scl_pin=14, address=None, i2c=None):
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        # Freenove utilise un bus I2C logiciel pour le LCD. Les broches par
        # defaut suivent son montage ESP32 (SDA 13 / SCL 14). Les GPIO 34 et
        # 35 de l'ESP32 classique sont des entrees uniquement et ne peuvent
        # donc pas piloter un bus I2C.
        self.i2c = i2c or machine.SoftI2C(
            sda=machine.Pin(sda_pin),
            scl=machine.Pin(scl_pin),
            freq=100000,
        )
        self.address = self._find_address() if address is None else address
        self._initialize()

    def _find_address(self):
        devices = self.i2c.scan()

        for address in (0x27, 0x3F):
            if address in devices:
                return address

        raise OSError(
            "LCD absent (adresses cherchees: 0x27/0x3F) sur SDA {} / SCL {}; "
            "scan={}".format(
                self.sda_pin,
                self.scl_pin,
                [hex(device) for device in devices],
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

        # Meme sequence que l'exemple Freenove: reveil du HD44780, puis
        # passage explicite en mode 4 bits avant sa configuration.
        self._command(0x33)
        sleep_ms(5)
        self._command(0x32)
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
        """Ecrit deux lignes, tronquees ou completees a 16 caracteres."""
        for row, line in enumerate((first_line, second_line)):
            self.set_cursor(0, row)
            # Certaines versions allegees de MicroPython n'implementent pas
            # str.ljust(). Le remplissage explicite reste compatible avec ces
            # firmwares tout en effacant la fin d'une ancienne ligne longue.
            line = str(line)[:16]
            self.write(line + " " * (16 - len(line)))

    def clear(self):
        self._command(self._CLEAR)

import os


class OV2640Camera:
    """Capture des images JPEG avec le module MicroPython ``camera``."""

    def __init__(self, photo_directory="/photos", camera_module=None):
        # L'import differe permet au reste du controleur de demarrer lorsqu'un
        # firmware sans prise en charge de la camera est installe.
        self.camera = camera_module or __import__("camera")
        self.photo_directory = photo_directory.rstrip("/") or "/"
        self._initialize()
        self._create_photo_directory()

    def _initialize(self):
        jpeg_format = getattr(self.camera, "JPEG", None)
        options = {} if jpeg_format is None else {"format": jpeg_format}
        result = self.camera.init(0, **options)
        if result is False:
            raise OSError("initialisation OV2640 impossible")

    def _create_photo_directory(self):
        if self.photo_directory == "/":
            return

        try:
            os.mkdir(self.photo_directory)
        except OSError:
            # mkdir echoue aussi lorsque le repertoire existe deja.
            os.listdir(self.photo_directory)

    def _next_path(self):
        filenames = os.listdir(self.photo_directory)
        number = 1
        while "photo_{:04d}.jpg".format(number) in filenames:
            number += 1
        return "{}/photo_{:04d}.jpg".format(
            self.photo_directory.rstrip("/"),
            number,
        )

    def capture(self):
        """Capture une image et retourne le chemin du fichier JPEG cree."""
        image = self.camera.capture()
        if not image:
            raise OSError("aucune image recue de l'OV2640")

        path = self._next_path()
        with open(path, "wb") as photo:
            photo.write(image)
        return path

    def deinit(self):
        """Libere la camera lorsqu'elle n'est plus utilisee."""
        self.camera.deinit()

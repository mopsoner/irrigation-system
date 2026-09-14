import os


class OV2640Camera:
    """Capture des images JPEG avec le module MicroPython ``camera``."""

    def __init__(self, photo_directory="/photos", camera_module=None):
        # L'import differe permet au reste du controleur de demarrer lorsqu'un
        # firmware sans prise en charge de la camera est installe.
        self.camera_module = camera_module or __import__("camera")
        self.camera = self._select_camera_api()
        self.photo_directory = photo_directory.rstrip("/") or "/"
        self._initialize()
        self._create_photo_directory()

    def _initialize(self):
        if self.camera is not self.camera_module:
            # L'API objet initialise le capteur dans Camera(). Les methodes
            # init() eventuelles de l'instance n'ont pas toutes la meme
            # signature que l'API fonctionnelle.
            return

        initializer = getattr(self.camera, "init", None)
        if initializer is None:
            # Certaines versions exposent une classe Camera deja initialisee
            # par son constructeur, sans methode init().
            return

        jpeg_format = getattr(self.camera_module, "JPEG", None)
        options = {} if jpeg_format is None else {"format": jpeg_format}
        result = initializer(0, **options)
        if result is False:
            raise OSError("initialisation OV2640 impossible")

    def _select_camera_api(self):
        """Accepte les API MicroPython fonctionnelle et orientee objet."""
        module = self.camera_module
        if callable(getattr(module, "init", None)) and callable(
            getattr(module, "capture", None)
        ):
            return module

        camera_class = getattr(module, "Camera", None)
        if callable(camera_class):
            instance = camera_class()
            if callable(getattr(instance, "capture", None)) or callable(
                getattr(instance, "snapshot", None)
            ):
                return instance

        raise RuntimeError(
            "module camera incompatible: API init/capture ou Camera requise; "
            "installer un firmware MicroPython avec le pilote OV2640"
        )

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
        capture = getattr(self.camera, "capture", None)
        if capture is None:
            capture = self.camera.snapshot
        image = capture()
        if not image:
            raise OSError("aucune image recue de l'OV2640")

        path = self._next_path()
        with open(path, "wb") as photo:
            photo.write(image)
        return path

    def deinit(self):
        """Libere la camera lorsqu'elle n'est plus utilisee."""
        deinitializer = getattr(self.camera, "deinit", None)
        if deinitializer is None:
            deinitializer = getattr(self.camera, "close", None)
        if deinitializer is not None:
            deinitializer()

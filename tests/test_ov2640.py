import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))

from cameras.ov2640 import OV2640Camera


class FakeCameraModule:
    JPEG = 7

    def __init__(self, image=b"jpeg-data", init_result=True):
        self.image = image
        self.init_result = init_result
        self.init_calls = []
        self.capture_calls = 0

    def init(self, camera_id, **options):
        self.init_calls.append((camera_id, options))
        return self.init_result

    def capture(self):
        self.capture_calls += 1
        return self.image

    def deinit(self):
        pass


class OV2640CameraTests(unittest.TestCase):
    def test_initializes_in_jpeg_mode_and_saves_numbered_photos(self):
        module = FakeCameraModule()

        with tempfile.TemporaryDirectory() as directory:
            camera = OV2640Camera(directory + "/photos", module)
            first_path = camera.capture()
            second_path = camera.capture()

            self.assertEqual(module.init_calls, [(0, {"format": module.JPEG})])
            self.assertEqual(pathlib.Path(first_path).read_bytes(), b"jpeg-data")
            self.assertEqual(pathlib.Path(second_path).name, "photo_0002.jpg")

    def test_rejects_failed_initialization(self):
        with self.assertRaisesRegex(OSError, "initialisation"):
            OV2640Camera(camera_module=FakeCameraModule(init_result=False))

    def test_rejects_an_empty_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            camera = OV2640Camera(directory + "/photos", FakeCameraModule(image=None))

            with self.assertRaisesRegex(OSError, "aucune image"):
                camera.capture()


if __name__ == "__main__":
    unittest.main()

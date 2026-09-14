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


class FakeObjectCamera:
    def __init__(self):
        self.closed = False

    def snapshot(self):
        return b"object-jpeg"

    def close(self):
        self.closed = True


class FakeObjectCameraModule:
    Camera = FakeObjectCamera


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

    def test_supports_the_class_based_camera_api(self):
        with tempfile.TemporaryDirectory() as directory:
            camera = OV2640Camera(directory + "/photos", FakeObjectCameraModule())
            path = camera.capture()
            camera.deinit()

            self.assertEqual(pathlib.Path(path).read_bytes(), b"object-jpeg")
            self.assertTrue(camera.camera.closed)

    def test_explains_when_the_camera_module_is_incompatible(self):
        with self.assertRaisesRegex(RuntimeError, "firmware MicroPython"):
            OV2640Camera(camera_module=object())


if __name__ == "__main__":
    unittest.main()

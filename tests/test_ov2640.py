import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "esp32"))

from cameras.ov2640 import OV2640Camera


JPEG_DATA = b"\xff\xd8jpeg-data\xff\xd9"


class FakeCameraModule:
    JPEG = 7

    def __init__(self, image=JPEG_DATA, init_result=True):
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
    def __init__(self, **options):
        self.closed = False
        self.options = options

    def snapshot(self):
        return JPEG_DATA

    def close(self):
        self.closed = True


class FakeObjectCameraModule:
    class PixelFormat:
        JPEG = 9

    class FrameSize:
        UXGA = 13

    Camera = FakeObjectCamera


class OV2640CameraTests(unittest.TestCase):
    def test_initializes_in_jpeg_mode_and_saves_numbered_photos(self):
        module = FakeCameraModule()

        with tempfile.TemporaryDirectory() as directory:
            camera = OV2640Camera(directory + "/photos", module)
            first_path = camera.capture()
            second_path = camera.capture()

            self.assertEqual(module.init_calls, [(0, {"format": module.JPEG})])
            self.assertEqual(pathlib.Path(first_path).read_bytes(), JPEG_DATA)
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

            self.assertEqual(pathlib.Path(path).read_bytes(), JPEG_DATA)
            self.assertEqual(
                camera.camera.options,
                {
                    "pixel_format": 9,
                    "frame_size": 13,
                    "xclk_freq": 20000000,
                },
            )
            self.assertTrue(camera.camera.closed)

    def test_object_api_falls_back_to_the_best_available_frame_size(self):
        class Module(FakeObjectCameraModule):
            class FrameSize:
                SVGA = 10
                VGA = 8

        camera = OV2640Camera(camera_module=Module())

        self.assertEqual(camera.camera.options["frame_size"], 10)

    def test_explains_when_the_camera_module_is_incompatible(self):
        with self.assertRaisesRegex(RuntimeError, "firmware MicroPython"):
            OV2640Camera(camera_module=object())

    def test_does_not_save_raw_pixels_with_a_jpg_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            photo_directory = pathlib.Path(directory) / "photos"
            camera = OV2640Camera(
                str(photo_directory),
                FakeCameraModule(image=b"\x10\xe3raw-pixels"),
            )

            with self.assertRaisesRegex(OSError, "capture non JPEG"):
                camera.capture()

            self.assertEqual(list(photo_directory.iterdir()), [])

    def test_accepts_pixformat_jpeg_constant_name(self):
        module = FakeCameraModule()
        module.PIXFORMAT_JPEG = module.JPEG
        module.JPEG = None

        with tempfile.TemporaryDirectory() as directory:
            OV2640Camera(directory + "/photos", module)

        self.assertEqual(module.init_calls, [(0, {"format": 7})])


if __name__ == "__main__":
    unittest.main()

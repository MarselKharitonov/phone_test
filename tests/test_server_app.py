import base64
import io
import unittest
from PIL import Image
from server.app import clean_image


class ImageChecks(unittest.TestCase):
    def test_image_is_decoded_and_normalized(self):
        source = io.BytesIO()
        Image.new("RGB", (4, 3), "red").save(source, "JPEG")
        result, size = clean_image(base64.b64encode(source.getvalue()).decode())
        self.assertEqual(size, (4, 3))
        self.assertTrue(result.startswith(b"\x89PNG"))

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            clean_image(base64.b64encode(b"not image").decode())

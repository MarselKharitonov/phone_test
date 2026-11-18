import tempfile
import unittest
from pathlib import Path
from stylist.contracts import Category, Frame, TryOnRequest
from stylist.gpt_image import GptImageProvider


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.person = root / "person.png"
        self.garment = root / "garment.png"
        self.person.touch()
        self.garment.touch()
        self.output = root / "output.png"

    def request(self, **kwargs):
        values = dict(person=self.person, garment=self.garment, output=self.output,
                      category=Category.TOPS, frame=Frame.WAIST)
        values.update(kwargs)
        return TryOnRequest(**values)

    def test_waist_rejects_bottoms(self):
        with self.assertRaises(ValueError):
            self.request(category=Category.BOTTOMS).validate()

    def test_full_accepts_bottoms(self):
        self.request(category=Category.BOTTOMS, frame=Frame.FULL).validate()

    def test_reject_input_as_output(self):
        with self.assertRaises(ValueError):
            self.request(output=self.person).validate()

    def test_reject_existing_output(self):
        self.output.touch()
        with self.assertRaises(ValueError):
            self.request().validate()

    def test_gpt_image_disabled(self):
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            GptImageProvider().generate(self.request())


if __name__ == "__main__":
    unittest.main()
